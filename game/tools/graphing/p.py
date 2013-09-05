



turns=0
graph={}
for l in open('l.txt'):
  sl=l.strip().split()
  if sl[1] not in graph:
    graph[sl[1]]={}
  if sl[3] not in graph[sl[1]]:
    graph[sl[1]][sl[3]]=[]
  graph[sl[1]][sl[3]].append( sl[-1] )
  turns=max(turns,int(sl[2]))



GNUPLOT='''
set term png
set title "%s"
set output "gnuplot.%s.png"
#plot "g.txt" using 1:2:3 title "stat+stat", "g.txt" using 1:3  title "post munge"
'''
GNUPLOTLINE='"gnuplot.%s.txt" using 1:%s with lines title "%s"'


for gname,ginfo in graph.items():

  fd=None
  headers=[]
  for t in range(1,turns):

    q=[`t-1`,]
    for n,l in sorted( ginfo.items() ):
#      print gname,n,l
      q.append( l[t-1] )
      if n not in headers: headers.append( n )
    if fd is None:
      fd=open('gnuplot.%s.txt'%(gname),'w')
      fd.write( '#'+' '.join( ['turn']+ginfo.keys() )+'\n' )
    fd.write( ' '.join(q)+'\n')
  fd.close()
  print headers
  fd=open('gnuplot.%s.run'%(gname),'w')
  fd.write(GNUPLOT%(gname,gname))
  fd.write('plot ')
  fd.write(','.join( [ GNUPLOTLINE%(gname,2+headers.index(hname),hname) for hname in headers ] ))
  fd.write('\n')
  fd.close()



