import os
import pydicom
import shutil
import re
from tqdm import tqdm

class DICOMWorkflowManager:
    def __init__(self, input_dir, output_dir=None):
        self.input_dir = input_dir
        self.output_dir = output_dir if output_dir else self._get_default_output_dir()

    def _get_default_output_dir(self):
        base_output_dir = os.path.join(self.input_dir + "_output")
        return self._get_unique_output_dir(base_output_dir)

    @staticmethod
    def sanitize_filename(filename):
        """파일명에서 빈칸과 특수문자를 제거 또는 변환하여 안전한 파일명을 반환합니다."""
        sanitized_name = re.sub(r'[<>:"/\\|?*]', '_', filename)
        sanitized_name = re.sub(r'\s+', '_', sanitized_name)
        return sanitized_name

    @staticmethod
    def _get_unique_output_dir(base_output_dir):
        """이미 존재하는 output 디렉토리를 피하기 위해 고유한 디렉토리 이름을 생성."""
        counter = 1
        output_dir = base_output_dir
        while os.path.exists(output_dir):
            output_dir = f"{base_output_dir}_{counter}"
            counter += 1
        return output_dir

    def process_dicom_files(self):
        """DICOM 파일을 SeriesDescription과 SliceThickness에 따라 폴더로 정렬"""
        os.makedirs(self.output_dir, exist_ok=True)
        subdirs = [root for root, dirs, files in os.walk(self.input_dir)]
        total_files = sum(len(files) for _, _, files in os.walk(self.input_dir))

        processed_files = 0
        for root in tqdm(subdirs, desc="Processing folders", unit="folder"):
            if root == self.input_dir:
                for file in os.listdir(root):
                    self._process_dicom_file(root, file)
                    processed_files += 1
                    yield f"처리 중... {processed_files}/{total_files} 파일 완료"
            else:
                subdir_name = os.path.basename(root)
                subdir_output_dir = os.path.join(self.output_dir, subdir_name)
                os.makedirs(subdir_output_dir, exist_ok=True)
                
                for file in os.listdir(root):
                    self._process_dicom_file(root, file, subdir_output_dir)
                    processed_files += 1
                    yield f"처리 중... {processed_files}/{total_files} 파일 완료"

    def _process_dicom_file(self, root, file, output_dir=None):
        """단일 DICOM 파일을 처리하여 SeriesDescription과 Slice Thickness에 따라 정렬"""
        try:
            if file.endswith('.dcm'):
                file_path = os.path.join(root, file)
                dicom_file = pydicom.dcmread(file_path)
                slice_thickness = getattr(dicom_file, 'SliceThickness', None)
                series_description = getattr(dicom_file, 'SeriesDescription', 'Unknown')
                
                if slice_thickness is None or slice_thickness == 0:
                    return
                
                folder_name = f"{self.sanitize_filename(series_description)}_{int(slice_thickness)}mm"
                thickness_dir = os.path.join(output_dir or self.output_dir, folder_name)
                os.makedirs(thickness_dir, exist_ok=True)
                
                sanitized_file = self.sanitize_filename(file)
                shutil.copy2(file_path, os.path.join(thickness_dir, sanitized_file))

        except Exception as e:
            print(f"파일 처리 중 오류 발생: {file}. 오류 내용: {str(e)}")

    def get_output_dir(self):
        """최종 출력 디렉토리 경로를 반환합니다."""
        return self.output_dir