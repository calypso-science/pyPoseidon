import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap, shiftgrid
import sys
from netCDF4 import Dataset
import matplotlib.dates as mdates
import urllib2, urllib
from get_point_map2 import get
#from get_point_map2 import get2
from get_point_map_hyflux import hget
from get_point_history2 import pget
import datetime
import pickle


#path0='/mnt/web/brey/2016H/'
#path1='/DATA/critechuser/2016/'
path0='/mnt/web/brey/venice/2015nc/'

def getmes(sdate,edate,point):

  pdate=min([edate+datetime.timedelta(hours=72),datetime.datetime.now()])


  url='http://webcritech.jrc.ec.europa.eu/SeaLevelsDb/Home/ShowBuoyData?id={}&dateMin={}%2F{:02d}%2F{:02d}+{:02d}%3A{:02d}&dateMax={}%2F{:02d}%2F{:02d}+{:02d}%3A{:02d}&field=&options='\
                                 .format(point,sdate.year,sdate.month,sdate.day,sdate.hour,0,pdate.year,pdate.month,pdate.day,pdate.hour,0)
  response=urllib2.urlopen(url)
  ls=response.readlines()
  lp=[elem.strip().split(',')  for elem in ls]

  # get lat lon
  c=[a.split(' ') for a in lp[1]][0]
  if 'lat' in c[2]: 
           plat=c[2].split('=')[1]
           idt=6
  else:
           c=[a.split(' ') for a in lp[2]][0]
           if 'lat' in c[2]: plat=c[2].split('=')[1]
           idt=7

  if 'lon' in c[3]: plon=c[3].split('=')[1]

  rt=[]
  vt=[]
  for a,b,c,d in lp[idt:]:
    rt.append(datetime.datetime.strptime(a,'%d %b %Y %H:%M:%S'))
    vt.append(d)

  return rt,vt,plat,plon


def view(date0,date1,basename,point):

  sdate=datetime.datetime.strptime(date0,'%Y%m%d.%H')
  edate=datetime.datetime.strptime(date1,'%Y%m%d.%H')

  fig = plt.figure(figsize=(10,8))
  ax = fig.add_axes([0.1,0.1,0.8,0.8])
  
  plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%d/%Y %H'))
  plt.gca().xaxis.set_major_locator(mdates.HourLocator(byhour=[0,12]))
  ax.xaxis_date()

  ## COMPARISON WITH MEASUREMENTS AND HYFLUX

  #get measurement data
  tp,hp,plat,plon=getmes(sdate,edate,point)

  if hp:
    plt.plot(tp,hp,'r-',linewidth=2,label='observed')
  else:
    print 'no measurements'

########################################################################
#   DELFT3D - map
########################################################################

  # get simulation data
  tdelft='20150101.00'
   
  if sdate < datetime.datetime.strptime(tdelft,'%Y%m%d.%H'):
     t1=tdelft
  else:
     t1=date0
  t2=date1

  tcw,cw=get(t1,t2,path0,basename,plat,plon)
  # check if on land
  if np.min(cw) != np.max(cw) :
    plt.plot(tcw[:-60],cw[:-60],'bo',markersize=7,label='DELFT3D - map')
    plt.plot(tcw[-61:],cw[-61:],'o',markerfacecolor='none', markeredgecolor='b', markersize=7,label='DELFT3D - map - forecast')
  else:
    print 'CONSTANT HEIGHT =',cw[0]
#--------------------------------------------------------------------------------------------------
  try:
  # check cold startup
   tcw1,cw1=get(t1,t2,path1,basename,plat,plon)
   if np.min(cw1) != np.max(cw1) :
     plt.plot(tcw1,cw1,'y--',linewidth=3,markersize=7,label='DELFT3D - map2')
  except:
     print 'error with map2'
     pass

#--------------------------------------------------------------------------------------------------

########################################################################
#   HYFLUX
########################################################################

  try:
  # read dictionary
   with open('hyfp.pkl', 'r') as f:
    hyfp=pickle.load(f)

   hlon,hlat = hyfp[int(point)]
   print 'Hyflux point = ',hlon,hlat

   tf,hf=hget(t1,t2,basename,hlat,hlon)
   plt.plot(tf[:-60],hf[:-60],'co-',markersize=7,linewidth=3,label='HYFLUX - map')
   plt.plot(tf[-61:],hf[-61:],'o--',markerfacecolor='none', markeredgecolor='c',markersize=7,linewidth=3,label='HYFLUX - map - forecast')
  except:
     print 'HYFLUX failed'
     pass

########################################################################
#   DELFT3D - his
########################################################################
  # read dictionary

  with open(path0+'1/1/00/med.pkl', 'r') as f:
    ptr=pickle.load(f)

  print ptr[int(point)]

  try:
  # plot
    hcw,hw=pget(t1,t2,path0,basename,ptr[int(point)])
    plt.plot(hcw[:-60*60],hw[:-60*60],'k-',linewidth=2,label='DELFT3D - his') # don't print the forecasting after 12 hours. Thus 60h *60m for total of 72 hours forecasting
    plt.plot(hcw[-61*61:],hw[-61*61:],'k--',linewidth=2,label='DELFT3D - his - forecasting')
  except:
     print 'DELFT3D his failed'
     pass

  #get measurement data if bpoint is different
# if int(bpoint) != int(point) :
#    print bpoint, point
#    btp,bhp,plat,plon=getmes(sdate,edate,bpoint)
#  # plt.plot(btp,bhp,'ro',markersize=2,label='observed 2')
#    plt.plot(btp,bhp,'g--',linewidth=2,label='observed 2')

  plt.gcf().autofmt_xdate()

  plt.legend(loc=0)

# plt.savefig('observed_'+str(point)+'.png',transparent=True)

  plt.show(block=False)

if __name__ == "__main__":
    date0=sys.argv[1]
    date1=sys.argv[2]
    basename=sys.argv[3]
    point=sys.argv[4]
    view(date0,date1,basename,point)

