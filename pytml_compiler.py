from ptml_tree import get_tree
import sys

if __name__ == '__main__':
    args = sys.argv[1:]
    try:
        in_file = args[0]
    except Exception:
        print 'File not provided'
        sys.exit(1)
    # determine
    try:
        out_file = args[1]
    except Exception:
        out_file = in_file.rsplit('.',1)[0]+'.html'
    print 'OUTPUT FILE:', out_file

    try:
        with open(in_file) as in_f:
            in_f.seek(0)
            data = in_f.read()
    except Exception:
        print "Unable to read from file"
        sys.exit(1)

    data = '\n'.join(map(lambda x: x.html(), get_tree(data)))
    try:
        with open(out_file,'w') as out_f:
            out_f.write(data)
    except Exception:
        print "Unable to write to file"
        sys.exit(1)
    print data
    
    
        
