import os

GOOGLEPLOT='''
      // Create the data table.
      var data = new google.visualization.DataTable();
data.addColumn('number', 'Turn');
      __HEADERS__


      data.addRows([
__LINES__
      ]);

      // Set chart options
      var options = {'title':'__TITLE__',
                     'width':900,
                     'height':300};

      // Instantiate and draw our chart, passing in some options.
      var chart = new google.visualization.LineChart(document.getElementById('__TITLE__'));
      chart.draw(data, options);

'''


GNUPLOT='''
set term png size 1200 500
set title "%s"
set xtics 1
set grid
set output "%s"

'''
GNUPLOTLINE='    "%s" using 1:%s with lines title "%s"'


#  logfile  title


def  mkgraph(srcdir,logfile,title):
  print 'plotting',(srcdir,logfile,title)
  turns=0
  graph={}
  for l in open(logfile):
    if not l.startswith('GRAPH'):
       continue
    sl=l.strip().split()
    if sl[1] not in graph:
      graph[sl[1]]={}
    if sl[2] not in graph[sl[1]]:
      graph[sl[1]][sl[2]]=[]
    graph[sl[1]][sl[2]].append( sl[-1] )
    turns=max(turns,int(sl[3]))

  graphs=''
  googlegraphs=[]
  for gname,ginfo in graph.items():
    goog={}
    goog['__TITLE__']=gname
    print gname
    plots=[]
    lines=[]
    for t in range(0,turns):
      line=[str(t)]
      for n,l in sorted( ginfo.items() ):
         if t==0: plots.append( [n,l] )
         line.append( str(l[t]) )
      lines.append( '  [ '+','.join( line )+' ],' )
    goog['__LINES__']='\n'.join( lines )
    goog['__HEADERS__']= '\n'.join( [ "data.addColumn('number', '%s');"%(n) for n,l in plots ] )
    t=GOOGLEPLOT
    for k,v in goog.items():
      t=t.replace(k,v)
    graphs+='\n\n'
    graphs+=t
    googlegraphs.append( goog )

  print 'writing',srcdir+'/google.%s.html'%(title)
  htmlfile=(srcdir+'/index.html')
  html=open('h.html').read().replace('__GRAPHS__',graphs)
  open(htmlfile,'w').write( html )

  return None

  for gname,ginfo in graph.items():
    print [[[title,gname]]]
    fd=None
    headers=[]
    datafile='gnuplot.%s.%s.txt'%(title,gname)
    pngfile=('gnuplot.%s.%s.png'%(title,gname) )
    htmlfile=('google.%s.%s.html'%(title,gname) )
    for t in range(0,turns):

      q=[`t`,]
      for n,l in sorted( ginfo.items() ):
        q.append( l[t-1] )
        if n not in headers: headers.append( n )
      if fd is None:
        fd=open(datafile,'w')
        fd.write( '#'+' '.join( ['turn']+ginfo.keys() )+'\n' )
      fd.write( ' '.join(q)+'\n')
    fd.close()
    script=GNUPLOT%(title+'     '+gname,pngfile)
    script+='\n'
    script+='plot    \\\n'
    script+=',\\\n'.join( [ GNUPLOTLINE%(datafile,2+headers.index(hname),hname) for hname in headers ] )
    script+='\n'
    fd=os.popen('gnuplot','w')
    fd.write(script)
    fd.close()


if __name__=="__main__":
  for f in os.listdir('.'):
     if f.startswith('gnuplot'):
        os.remove(f)
  for dpath,subd,subf in os.walk('../../save.test'):
     print dpath,subf
     for f in subf:
       if f=='message.log':
         mkgraph(dpath,dpath+'/'+f,dpath.split(os.sep)[-1])


