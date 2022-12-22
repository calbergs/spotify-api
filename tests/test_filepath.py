import os

outdir = '/spotify/spotify_data'
outname = 'name.csv'

if not os.path.exists(outdir):
    print('Path does not exist')
else:
    print('Path exists')