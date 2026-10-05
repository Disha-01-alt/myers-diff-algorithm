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
    n=len(a)
    m=len(b)
    edits=[]

    offset=(n+m)//2+2
    v_fwd=[-1]*(2*offset)
    v_bwd=[-1]*(2*offset)

    def find_middle_snake(a_lo,a_hi,b_lo,b_hi):
        n=a_hi-a_lo
        m=b_hi-b_lo
        delta=n-m
        max_d=(n+m+1)//2
        v_fwd[offset+1]=0
        v_bwd[offset+1]=0

        for d in range(max_d+1):
            for k in range(-d,d+1,2):
                if k==-d or (k!=d and v_fwd[offset+k-1]<v_fwd[offset+k+1]):
                    x=v_fwd[offset+k+1]
                else:
                    x=v_fwd[offset+k-1]+1
                y=x-k
                x1=x
                y1=y
                while x<n and y<m and a[a_lo+x]==b[b_lo+y]:
                    x+=1
                    y+=1
                v_fwd[offset+k]=x
                rev_k=delta-k
                if delta%2!=0 and -(d-1)<=rev_k<=d-1 and x+v_bwd[offset+rev_k]>=n:
                    return (2*d-1,a_lo+x1,b_lo+y1,a_lo+x,b_lo+y)
            for k in range(-d,d+1,2):
                if k==-d or (k!=d and v_bwd[offset+k-1]<v_bwd[offset+k+1]):
                    x=v_bwd[offset+k+1]
                else:
                    x=v_bwd[offset+k-1]+1
                y=x-k
                x1=x
                y1=y
                while x<n and y<m and a[a_hi-1-x]==b[b_hi-1-y]:
                    x+=1
                    y+=1
                v_bwd[offset+k]=x
                rev_k=delta-k
                if delta%2==0 and -d<=rev_k<=d and x+v_fwd[offset+rev_k]>=n:
                    return (2*d,a_hi-x,b_hi-y,a_hi-x1,b_hi-y1)
        return None

    def diff_range(a_lo,a_hi,b_lo,b_hi):
        n=a_hi-a_lo
        m=b_hi-b_lo
        if n==0:
            for j in range(b_lo,b_hi):
                edits.append(("ins",b[j]))
            return
        if m==0:
            for i in range(a_lo,a_hi):
                edits.append(("del",a[i]))
            return

        dist,x1,y1,x2,y2=find_middle_snake(a_lo,a_hi,b_lo,b_hi)
        if dist>1:
            diff_range(a_lo,x1,b_lo,y1)
            i=x1
            j=y1
            while i<x2 and j<y2:
                edits.append(("keep",a[i]))
                i+=1
                j+=1
            diff_range(x2,a_hi,y2,b_hi)
        else:
            i=a_lo
            j=b_lo
            while i<a_hi and j<b_hi and a[i]==b[j]:
                edits.append(("keep",a[i]))
                i+=1
                j+=1
            if a_hi-i>b_hi-j:
                edits.append(("del",a[i]))
                i+=1
            elif b_hi-j>a_hi-i:
                edits.append(("ins",b[j]))
                j+=1
            while i<a_hi and j<b_hi:
                edits.append(("keep",a[i]))
                i+=1
                j+=1

    prefix=0
    while prefix<n and prefix<m and a[prefix]==b[prefix]:
        prefix+=1
    suffix=0
    while suffix<n-prefix and suffix<m-prefix and a[n-1-suffix]==b[m-1-suffix]:
        suffix+=1
    for i in range(prefix):
        edits.append(("keep",a[i]))
    diff_range(prefix,n-suffix,prefix,m-suffix)
    for i in range(n-suffix,n):
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