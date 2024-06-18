import moxing as mox

# src 起点 dst 目的地    from obs

src_url = "obs://computer-vision-lungtest/lung_data.zip"
dst_url = "./lung"

mox.file.copy_parallel(src_url, dst_url)

