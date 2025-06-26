import subprocess
import os

input_root_folder = "/home/zxl/data/EFAlignment/mp4"
file = "video.mp4"
dvs_exposure = "duration" 
output_folder = "/home/zxl/data/EFAlignment/v2e"
name = "events.txt"
# width = 346, height = 260 DAVIS
width = 346
height = 260

def run_cmd(cmd_args):
    try:
        # 执行命令并捕获输出
        result = subprocess.run(
            cmd_args,
            capture_output=True,  # 捕获 stdout/stderr
            text=True,            # 输出转为字符串
            check=True            # 非零返回码时抛出异常
        )
        print("✅success, the output goes:", result.stdout)

    except subprocess.CalledProcessError as e:
        print(f"❌fail (返回码 {e.returncode}):")
        print(f"错误详情: {e.stderr}") 

    except FileNotFoundError:
        print(f"🚫 找不到文件或命令: {cmd_args[0]}")

    except Exception as e:
        print(f"⚠️ 未知错误: {str(e)}")
        
import shutil

def run_v2e(input_root_folder, filename):
    output_dir = os.path.join(output_folder, filename)
    input_dir = os.path.join(input_root_folder, filename)
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
    # if os.path.exists(os.path.join(output_dir, "events_npz")): # 删除生成的npz文件，没有生成错误就不要轻易用
    #     shutil.rmtree(os.path.join(output_dir, "events_npz"))   
    #     print(os.path.join(output_dir, "events_npz"))
    if dvs_exposure == "duration":
        # arg1 = 0.005
        arg1 = 1 / 30 # avi视频帧率是正常速度
    elif dvs_exposure == "count":
        arg1 = 5000
    cmd_args = [
        "python", "v2e.py",
        "-i", os.path.join(input_dir, file), 
        "--overwrite",
        "--timestamp_resolution=0.003",
        "--auto_timestamp_resolution=False",
        "--dvs_exposure", dvs_exposure, str(arg1),
        "--output_folder", output_dir,
        "--pos_thres=0.15",
        "--neg_thres=0.15",
        "--sigma_thres=0.03",
        # "--dvs_text", name,
        "--dvs_npz=True",
        "--output_width=" + str(width),
        "--output_height=" + str(height),
        # "--stop_time=1", # for test
        "--cutoff_hz=15",
        "--skip_video_output",
        "--no_preview"
    ]
    run_cmd(cmd_args)
    


def run_avi_2_mp4(filename):
    input_file = os.path.join(output_folder, filename, "dvs-video.avi")
    output_file = os.path.join(output_folder, filename, "dvs-video.mp4")
    cmd_args = [
        "ffmpeg",
        "-i",input_file,
        "-c:v",
        "copy",
        "-c:a",
        "copy",
        "-y",
        output_file
    ]
    run_cmd(cmd_args)

if __name__ == "__main__":
    for video_name in os.listdir(input_root_folder):
        print("try video_name:", video_name)
        run_v2e(input_root_folder, video_name)
        run_avi_2_mp4(video_name)
        # break
        
     
     