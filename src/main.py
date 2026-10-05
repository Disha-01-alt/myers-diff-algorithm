import sys

def read_file(path):
    try:
        with open(path,"rb") as f:
            content=f.read()
    except Exception as e:
        sys.stderr.write(f"Error reading file {path}: {e}\n")
        sys.exit(2)

    if not content:
        return []

    lines=content.split(b"\n")
    if lines and lines[-1]==b"":
        lines.pop()
    return lines

def myers_algo(a,b):
    na=len(a)
    nb=len(b)
    edits=[]

    def middle_snake(a0,a1,b0,b1):
        n=a1-a0
        m=b1-b0
        delta=n-m
        maxd=(n+m+1)//2
        vf={1:0}
        vb={1:0}

        for d in range(maxd+1):
            for k in range(-d,d+1,2):
                if k==-d or (k!=d and vf.get(k-1,-1)<vf.get(k+1,-1)):
                    x=vf[k+1]
                else:
                    x=vf[k-1]+1
                y=x-k
                x0=x
                y0=y
                while x<n and y<m and a[a0+x]==b[b0+y]:
                    x+=1
                    y+=1
                vf[k]=x
                inv=delta-k
                if delta%2!=0 and -(d-1)<=inv<=d-1 and x+vb.get(inv,-1)>=n:
                    return (2*d-1,a0+x0,b0+y0,a0+x,b0+y)
            for k in range(-d,d+1,2):
                if k==-d or (k!=d and vb.get(k-1,-1)<vb.get(k+1,-1)):
                    u=vb[k+1]
                else:
                    u=vb[k-1]+1
                w=u-k
                u0=u
                w0=w
                while u<n and w<m and a[a1-1-u]==b[b1-1-w]:
                    u+=1
                    w+=1
                vb[k]=u
                inv=delta-k
                if delta%2==0 and -d<=inv<=d and u+vf.get(inv,-1)>=n:
                    return (2*d,a1-u,b1-w,a1-u0,b1-w0)
        return None

    def rec(a0,a1,b0,b1):
        n=a1-a0
        m=b1-b0
        if n==0:
            for j in range(b0,b1):
                edits.append(("ins",b[j]))
            return
        if m==0:
            for i in range(a0,a1):
                edits.append(("del",a[i]))
            return

        d,xs,ys,xe,ye=middle_snake(a0,a1,b0,b1)
        if d>1:
            rec(a0,xs,b0,ys)
            i=xs
            j=ys
            while i<xe and j<ye:
                edits.append(("keep",a[i]))
                i+=1
                j+=1
            rec(xe,a1,ye,b1)
        else:
            i=a0
            j=b0
            while i<a1 and j<b1 and a[i]==b[j]:
                edits.append(("keep",a[i]))
                i+=1
                j+=1
            if a1-i>b1-j:
                edits.append(("del",a[i]))
                i+=1
            elif b1-j>a1-i:
                edits.append(("ins",b[j]))
                j+=1
            while i<a1 and j<b1:
                edits.append(("keep",a[i]))
                i+=1
                j+=1

    p=0
    while p<na and p<nb and a[p]==b[p]:
        p+=1
    s=0
    while s<na-p and s<nb-p and a[na-1-s]==b[nb-1-s]:
        s+=1
    for i in range(p):
        edits.append(("keep",a[i]))
    rec(p,na-s,p,nb-s)
    for i in range(na-s,na):
        edits.append(("keep",a[i]))
    return edits

def format_ranges(indices):
    if not indices:
        return "."

    unique_sorted=sorted(set(indices))
    ranges=[]
    start=unique_sorted[0]
    end=start+1

    for idx in unique_sorted[1:]:
        if idx==end:
            end+=1
        else:
            ranges.append(f"{start}-{end}")
            start=idx
            end=idx+1

    ranges.append(f"{start}-{end}")
    return ",".join(ranges)

def highlight_pair(line_a,line_b):
    try:
        chars_a=list(line_a.decode("utf-8"))
        chars_b=list(line_b.decode("utf-8"))
    except UnicodeDecodeError:
        chars_a=[chr(b) for b in line_a]
        chars_b=[chr(b) for b in line_b]

    edits=myers_algo(chars_a,chars_b)

    del_idx=[]
    ins_idx=[]
    ia=0
    ib=0

    for op,_ in edits:
        if op=="keep":
            ia+=1
            ib+=1
        elif op=="del":
            del_idx.append(ia)
            ia+=1
        elif op=="ins":
            ins_idx.append(ib)
            ib+=1

    return f"? {format_ranges(del_idx)} | {format_ranges(ins_idx)}"

def main():
    if len(sys.argv)!=4 or sys.argv[1] not in ("lines","highlight"):
        sys.stderr.write("usage: main.py lines|highlight A_PATH B_PATH\n")
        return 2

    mode,path_a,path_b=sys.argv[1:]

    lines_a=read_file(path_a)
    lines_b=read_file(path_b)

    line_edits=myers_algo(lines_a,lines_b)

    i=0
    n=len(line_edits)

    while i<n:
        op,val=line_edits[i]

        if op=="keep":
            sys.stdout.buffer.write(b" "+val+b"\n")
            i+=1
        else:
            dels=[]
            inss=[]

            while i<n and line_edits[i][0]!="keep":
                cop,cval=line_edits[i]

                if cop=="del":
                    dels.append(cval)
                else:
                    inss.append(cval)

                i+=1

            for d in dels:
                sys.stdout.buffer.write(b"-"+d+b"\n")

            p_len=min(len(dels),len(inss))

            for idx,ins in enumerate(inss):
                sys.stdout.buffer.write(b"+"+ins+b"\n")

                if mode=="highlight" and idx<p_len:
                    hl=highlight_pair(dels[idx],ins)
                    sys.stdout.buffer.write(hl.encode("utf-8")+b"\n")

    return 0

if __name__=="__main__":
    raise SystemExit(main())