import sys

def read_file(path):
    try:
        with open(path,"rb") as f:
            content=f.read()
    except Exception as e:
        sys.stderr.write(f"Error reading file {path}: {e}\n")
        sys.exit(2)
    lines=content.split(b"\n")
    if lines and lines[-1]==b"":
        lines.pop()
    return lines

def myers_algo(a,b):
    n=len(a)
    m=len(b)
    MAX=n+m
    if MAX==0:
        return []
    V={1:0}
    trace=[]
    for d in range(MAX+1):
        V_copy=V.copy()
        trace.append(V_copy)
        for k in range(-d,d+1,2):
            if k==-d or (k!=d and V.get(k-1,-1)<V.get(k+1,-1)):
                x=V[k+1]
            else:
                x=V[k-1]+1
            y=x-k
            while x<n and y<m and a[x]==b[y]:
                x+=1
                y+=1
            V[k]=x
            if x>=n and y>=m:
                return backtrack_path(a,b,trace,n,m)
    return []

def backtrack_path(a,b,trace,n,m):
    x,y=n,m
    edits=[]
    for d in range(len(trace)-1,-1,-1):
        V=trace[d]
        k=x-y
        if d==0:
            while x>0 and y>0:
                x-=1
                y-=1
                edits.append(("keep",a[x]))
            break
        if k==-d or (k!=d and V.get(k-1,-1)<V.get(k+1,-1)):
            prev_k=k+1
        else:
            prev_k=k-1
        prev_x=V[prev_k]
        prev_y=prev_x-prev_k
        while x>prev_x and y>prev_y:
            x-=1
            y-=1
            edits.append(("keep",a[x]))
        if d>0:
            if x==prev_x:
                y-=1
                edits.append(("ins",b[y]))
            else:
                x-=1
                edits.append(("del",a[x]))
    edits.reverse()
    return edits

def main() -> int:
    if len(sys.argv) != 4 or sys.argv[1] not in ("lines", "highlight"):
        sys.stderr.write("usage: main.py lines|highlight A_PATH B_PATH\n")
        return 2

    mode, path_a, path_b = sys.argv[1:]
    lines_a = read_file(path_a)
    lines_b = read_file(path_b)

    line_edits = myers_algo(lines_a, lines_b)
    i=0
    n=len(line_edits)
    while i<n:
        op,val=line_edits[i]
        if op=="keep":
            sys.stdout.buffer.write(b" "+val+b"\n")
            i+=1
        else:
            dels,inss=[],[]
            while i<n and line_edits[i][0]!="keep":
                cop,cval=line_edits[i]
                if cop=="del":
                    dels.append(cval)
                else:
                    inss.append(cval)
                i+=1
            for d in dels:
                sys.stdout.buffer.write(b"-"+d+b"\n")
            for ins in inss:
                sys.stdout.buffer.write(b"+"+ins+b"\n")

    return 0

raise SystemExit(main())