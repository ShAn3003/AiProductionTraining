import moxing as mox

# src 起点 dst 目的地    from obs

src_url = "../datafile.csv"
dst_url = "obs://lungnudulesdata/datafile.csv"

mox.file.copy_parallel(src_url, dst_url)

