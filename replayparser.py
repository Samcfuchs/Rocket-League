#!/home/sam/miniconda3/envs/datasci/bin/python
import matplotlib.pyplot as plt
import json
import numpy as np
import pandas as pd
import sys
from collections import Counter

class TwoBallsError(Exception):
    def __init__(self, message="", frame=0):
        self.frame = frame
        self.message = message
        super().__init__(self.message)

"""
Generate a dataframe of every RigidBody update, tagged with the frame, time, the
point in which the update occurred, and the id of the updated actor.
"""
def get_updates(data):
    goal_frames = [g['frame'] for g in data['properties']['Goals']]
    scorers = [g['PlayerTeam'] for g in data['properties']['Goals']]
    frames = data['network_frames']['frames']
    updates = []
    point = 0
    scorer = scorers[0]
    for i,f in enumerate(frames):
        ua = f['updated_actors']
        if i in goal_frames:
            point += 1
            scorer = scorers[point] if point < len(scorers) else 0.5
        for prop in ua:
            if 'RigidBody' in prop['attribute'].keys():
                updates.append({
                    'f': i,
                    't': f['time'],
                    'pt': point,
                    'id': prop['actor_id'],
                    'scorer': scorer
                })
    
    return updates

"""
Taking as input a dataframe of updates, identify key actor IDs for extraction
"""
def identify_objects(update_df):
    actor_ids = [{}] * (update_df.pt.max() + 1)

    for pt in range(0, update_df.pt.max() + 1):
        sub = update_df.loc[update_df.pt==pt]
        c = Counter(sub.id).most_common(5)
        actor_ids[pt] = {'ball': c[0][0]}

    return actor_ids


def get_ball_info(data, actor_ids):

    ball_ids = [a['ball'] for a in actor_ids]

    frames = data['network_frames']['frames']

    ball_data = []

    scorers = [g['PlayerTeam'] for g in data['properties']['Goals']]
    goal_frames = [g['frame'] for g in data['properties']['Goals']]

    def is_ball_actor(updated_actor, curr_id):
        return (updated_actor['actor_id'] == curr_id and 
            'RigidBody' in updated_actor['attribute'].keys())

    n = 0
    for i, f in enumerate(frames):
        if i in goal_frames:
            n += 1
        
        if n >= len(scorers):
            scorer = 0.5
        else:
            scorer = scorers[n]
        
        ua = f['updated_actors']
        if not ua: continue

        ball_prop = [prop for prop in ua if is_ball_actor(prop, ball_ids[n])]
        if not ball_prop: continue

        # If there's two ball updates in the same frame we have a big problem
        try:
            assert len(ball_prop) == 1
        except AssertionError:
            raise TwoBallsError(frame=i)

        ball_prop = ball_prop[0]

        loc = ball_prop['attribute']['RigidBody']['location']
        vel = ball_prop['attribute']['RigidBody']['linear_velocity']
        if vel is None: vel = {'x':0, 'y':0, 'z':0}


        ball_data.append({
            'f': i,
            'ix': ball_prop['actor_id'],
            't': f['time'],
            'x': loc['x'],
            'y': loc['y'],
            'z': loc['z'],
            'dx': vel['x'],
            'dy': vel['y'],
            'dz': vel['z'],
            'scorer': scorer,
            'pt': n,
            'month': data['properties']['Date'].split('-')[1]
        })
    
    return ball_data


if __name__ == "__main__":

    input_filename = "data/1.json"
    if len(sys.argv) > 1:
        input_filename = sys.argv[0]

    with open(input_filename, 'r') as f:
        j = json.load(f)
        data = j
        frames = j['network_frames']['frames']

    updates_df = pd.DataFrame.from_records(get_updates(data))

    actor_ids = identify_objects(updates_df)
    print(actor_ids)

    # This retrieves the final list of all ball velocities.
    balls = get_ball_info(data, actor_ids)
    balls_df = pd.DataFrame.from_records(balls)

    # Now we need to label those with goal outcomes
    balls_df['scorer'] = updates_df['scorer']
    print(balls_df.head())

