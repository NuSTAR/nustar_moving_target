
def download_tle(outdir='./'):
    """Download the NuSTAR TLE archive.
    
    Parameters
    ----------
    
    outdir: Optional desired output location. Defaults to the working directory.
    
    Returns
    ----------
    
    Returns the filename that you've downloaded.
    
    Notes
    ---------
    
    """
    import os
    import wget


    # Make sure you've got a trailing slash...
    if not(outdir.endswith('/')):
        outdir+'/'
    
    # Make sure the directory exists and create one if not.
    directory = os.path.dirname(outdir)
    if not os.path.exists(directory):
        os.makedirs(directory)
    
    myname='nustar_pysolar.io.download_tle'
    
    url='http://www.srl.caltech.edu/NuSTAR_Public/NuSTAROperationSite/NuSTAR.tle'

    # Check to see if the file exists:
    fname = 'NuSTAR.tle'
    outfile = outdir+'/'+fname
    if (os.path.isfile(outfile)):
        os.remove(outfile)
    
    wget.download(url, out=outfile)
    
    return outfile

def read_tle_file(tlefile, **kwargs):
    """Read in the TLE file. 
    
    Returns the times for each line element and the TLE time
    
    """
    times = []
    line1 = []
    line2 = []
    
    from datetime import datetime
    # Catch if the file can't be opened:
    try:
        f = open(tlefile, 'r')
    except FileNotFoundError:
        print("Unable to open: "+tlefile)
    
    ln=0
    for line in f:
#        print(line)
        if (ln == 0):
            year= int(line[18:20])
            day = int(line[20:23])
            
            times.extend([datetime.strptime("{}:{}".format(year, day), "%y:%j")])
            line1.extend([line.strip()])
            ln=1
        else:
            ln=0
            line2.extend([line.strip()])
    f.close()
    return times, line1, line2

def get_epoch_tle(epoch, tlefile):
    """Find the TLE that is closest to the epoch you want to search.
    
    epoch is a datetime object, tlefile is the file you want to search through.
    
    """

    times, line1, line2 = read_tle_file(tlefile)
    from astropy.time import Time
    
    # Allow astropy Time objects
    if type(epoch) is Time:
        epoch = epoch.datetime
        
    mindt = 100.
    min_ind = 0
    for ind, t in enumerate(times):
        dt = abs((epoch -t).days)
        if dt < mindt:
            min_ind = ind
            mindt = dt

    good_line1 = line1[min_ind]
    good_line2 = line2[min_ind]

    return mindt, good_line1, good_line2





def parse_occ(file):
    import pandas as pd
    from datetime import datetime


    '''Parse the occultation file that you generated usisng the orbit_model/occ script'''
    
    df = pd.read_csv(file, delim_whitespace=True, header=None, skiprows=6,
                     names = ['ingress', 'ingress_ang', 'midpoint_eng', 'midpoint_ang',
                              'egress', 'egress_ang'])

    df['visible'] = df['egress']
    df['occulted'] = df['egress']

    for ind in range(len(df)):
        if ind == len(df) -1:
            break
        df.loc[ind,('visible')] = datetime.strptime(
                df.loc[ind, ('egress')],
                '%Y:%j:%H:%M:%S')
        df.loc[ind,('occulted')] = datetime.strptime(
            df.loc[ind+1, ('ingress')],
            '%Y:%j:%H:%M:%S')
    
    orbits = df.loc[0:len(df)-2, ('visible', 'occulted')]
    return orbits
    

def parse_pa(file):
    '''Parse the output PA string that you generated usisng the orbit_model/occ script
    
    This should have exactly one line of the format: 
    
    Position angle: 43.608806 [deg]
    
    '''
    
    f = open(file)
    for line in f:
        fields = line.split()
        mps_pa = float(fields[2])
    
    # Remember that the mission planning PA is 180 degrees off from the SKY PA:
    
    sky_pa = 180 - mps_pa
        
    return sky_pa
