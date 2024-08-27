from flask import Flask, render_template, jsonify, request, Response
import os
from workflow_manager import DICOMWorkflowManager
import json

app = Flask(__name__)
app.secret_key = 'your_secret_key'

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        input_dir = request.form['input_dir'].strip()
        output_dir = request.form.get('output_dir', '').strip()
        
        if not os.path.isdir(input_dir):
            return jsonify({"success": False, "message": f"입력된 경로가 존재하지 않습니다: {input_dir}"})

        if output_dir and not os.path.isdir(output_dir):
            try:
                os.makedirs(output_dir)
            except OSError:
                return jsonify({"success": False, "message": f"출력 디렉토리를 생성할 수 없습니다: {output_dir}"})

        def generate():
            try:
                workflow_manager = DICOMWorkflowManager(input_dir, output_dir)
                for progress in workflow_manager.process_dicom_files():
                    yield json.dumps({"progress": progress}) + '\n'
                
                final_output_dir = workflow_manager.get_output_dir()
                yield json.dumps({"result": {"success": True, "message": f'DICOM 파일 정렬이 완료되었습니다. 출력 디렉토리: {final_output_dir}'}}) + '\n'
            except Exception as e:
                yield json.dumps({"result": {"success": False, "message": f'DICOM 파일 처리 중 오류가 발생했습니다: {str(e)}'}}) + '\n'

        return Response(generate(), content_type='application/json')
    
    return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True)