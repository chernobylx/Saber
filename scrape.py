import pybaseball as pb
def scrape_statcast(year, output_dir: str = 'data/statcast'):
    df = pb.statcast(str(year)+"-02-01", str(year)+"-11-30")
    df.to_csv(output_dir+'/statcast_'+str(year)+'.csv', index=False)

