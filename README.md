# Rocket League Replay Analytics

## Get replay files
Replay files are hosted on octane.gg, which links from ballchasing.com. 
These should be loaded into ./replays (or a subfolder in there).

## Parse replay files
I use rrrocket. That seems to generate slightly more usable files. I can parse
replays with this command:

    ./rrrocket -nm ./replays
    mv ./replays/*.json data

## Parse rrrocket files to motion data
I can do this with ./parser.py to get the data for any single rrrocket output
file. I'm working on pipelining this to gather multiple replays at once.

## Understanding motion data

It seems like the positional data is stored on either of two scales: X can max
out at either 109 or 11,909. This makes it...impossible to compare replays
reliably? I think this might be a versioning thing--maybe new replays are on a
different scale from old ones.

It turns out all the replays from June are simply botched. So I'll have to throw
those out for analysis, probably. I could probably scale them to match, but the
bigger question is whether it's really worth pushing forward with this
particular set of 45 replays. They're not that good, and I don't have a ton of
faith that a model could make sense of them. Importantly, they're in a lot of
different game modes, which probably makes this even more confusing. Ultimately,
I should probably move over to analyzing RLCS replays instead.

There's still some unsolved data issues. First, I know for a fact that I'm not
handling overtimes correctly. The play up to 0 seconds is classified with
whoever wins the overtime, even though that point ends with a no-decision and
the overtime starts in a different play.

Second, there are a bunch of points that end with the ball just in the middle
of the field. There are two cases where this makes sense (end of regular time, forfeit).
This is possible since the way we define `pts`, those plays are part of a new
point that just doesn't end with a winner, and we assign them the class 0.5. But
we also see some of these points which are assigned a winning team. That seems
very wrong. If the ball doesn't end in the goal, how can a team have scored?

