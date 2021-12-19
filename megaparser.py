from matplotlib import pyplot as plt
import pandas as pd
import sys
import replayparser as parser
import json
import os
from tqdm import tqdm

if __name__ == "__main__":
    if len(sys.argv) == 1:
        input_folder = "data/RLCS21"
        output_file = "parsed/pros.json"
    else:
        input_folder = sys.argv[1]
        output_folder = sys.argv[2]

    is_replay = lambda n: 'replay' in n.split('.')
    filenames = list(filter(is_replay, os.listdir(input_folder)))
    allballs = []

    for fname in tqdm(filenames):
        with open(f"{input_folder}/{fname}", 'r') as f:
            j = json.load(f)
            data = j
            frames = data['network_frames']['frames']
        
        #print(data['game_type'])
        
        updates_df = pd.DataFrame.from_records(parser.get_updates(data))
        actor_ids = parser.identify_objects(updates_df)
        try:
            balls = parser.get_ball_info(data, actor_ids)
        except parser.TwoBallsError as e:
            print(fname)
            plt.title(fname)
            plt.scatter(updates_df.f, updates_df.id, c=updates_df.pt, s=1)
            plt.axvline(e.frame)
            plt.show()


        id = data['properties']['Id']

        for rec in balls:
            rec['id'] = id
        allballs += balls    

    print(len(allballs))

    pd.DataFrame(allballs).to_json(output_file)
    
