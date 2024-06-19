import moxing as mox

# src 起点 dst 目的地    from obs

src_url = "/home/ma-user/work/AiProductionTraining/src/LungNudulesDetect/10_epoches_test10/weights/last.pt"
dst_url = "obs://lungnudulesdata/yolov8.pt"

mox.file.copy_parallel(src_url, dst_url)

