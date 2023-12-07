from dbr import *
import cv2
import numpy as np

class BarCodeScanner:
    def __init__(self):
        self.barcodeList = []
        self.drawStack = []

    def text_results_callback_func(self, frame_id, t_results, user_data):
        for result in t_results:
            text_result = TextResult(result)
            self.drawStack.append(text_result.localization_result.localization_points)

            if text_result is not None and text_result.barcode_text not in self.barcodeList and text_result.barcode_format_string == "UPC_A":
                print(f"Barcode Format : {text_result.barcode_format_string}")
                print(f"Barcode Text : {text_result.barcode_text}")
                print(f"Localization Points : {text_result.localization_result.localization_points}")
                if text_result.exception:
                    print(f"Exception : {text_result.exception}")
                print("-------------")
                self.barcodeList.append(text_result.barcode_text)

    def intermediate_results_callback_func(self, frame_id, i_results, user_data):
        print(frame_id)
        for result in i_results:
            intermediate_result = IntermediateResult(result)
            print('Intermediate Result data type : {0}'.format(intermediate_result.result_type))
            print('Intermediate Result data : {0}'.format(intermediate_result.results))
            print("-------------")

    def error_callback_func(self, frame_id, error_code, user_data):
        print(frame_id)
        error_msg = user_data.get_error_string(error_code)
        print('Error : {0} ; {1}'.format(error_code, error_msg))

    def run_decode_video(self):
        video_width = 1280
        video_height = 720
        drawAgain = False

        # a. Decode video from camera
        cap = cv2.VideoCapture(3)
        cap2 = cv2.VideoCapture(2)

        # Decode video file
        # video_file = "Put your video file path here."
        # vc = cv2.VideoCapture(video_file)

        cap.set(cv2.CAP_PROP_FRAME_WIDTH, video_width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, video_height)
        cap2.set(cv2.CAP_PROP_FRAME_WIDTH, video_width)
        cap2.set(cv2.CAP_PROP_FRAME_HEIGHT, video_height)

        stride = 0
        if cap.isOpened():
            rval, frame = cap.read()
            stride = frame.strides[0]
        else:
            return

        stride2 = 0
        if cap2.isOpened():
            rval2, frame2 = cap2.read()
            stride2 = frame2.strides[0]
        else:
            return

        reader = BarcodeReader.get_instance()
        if reader == None:
            raise BarcodeReaderError("Get instance failed")
        parameters = reader.init_frame_decoding_parameters()
        parameters.max_queue_length = 30
        parameters.max_result_queue_length = 30
        parameters.width = video_width
        parameters.height = video_height
        parameters.stride = stride
        parameters.image_pixel_format = EnumImagePixelFormat.IPF_RGB_888
        parameters.region_top = 0
        parameters.region_bottom = 100
        parameters.region_left = 0
        parameters.region_right = 100
        parameters.region_measured_by_percentage = 1
        parameters.threshold = 0.01
        parameters.fps = 15
        parameters.auto_filter = 1

        # start video decoding. The callback function will receive the recognized barcodes.
        reader.start_video_mode(parameters, self.text_results_callback_func)

        # # start video decoding. Pass three callbacks at the same time.
        # reader.start_video_mode(parameters, text_results_callback_func, "", intermediate_results_callback_func, error_callback_func, reader)

        while True:
            frame2Resized = cv2.resize(frame2,(frame.shape[0],frame.shape[1]))
            numpy_horizontal = np.vstack((frame, frame2))
            if drawAgain:
                drawAgain = False
                cv2.rectangle(numpy_horizontal, rect[0], rect[2], (0, 255, 0), 3)
            if self.drawStack:
                rect = self.drawStack.pop(0)
                cv2.rectangle(numpy_horizontal, rect[0], rect[2], (0,255,0), 3)
                drawAgain = True


            cv2.imshow("Video Barcode Reader", numpy_horizontal)

            rval, frame = cap.read()
            rval2, frame2 = cap2.read()
            if rval is False or rval2 is False:
                break

            try:
                # append frame to video buffer cyclically
                ret = reader.append_video_frame(frame)
                ret2 = reader.append_video_frame(frame2)
            except:
                pass

            # 'ESC' for quit
            key = cv2.waitKey(1)
            if key == 27 or key == ord('c'):
                break

        reader.stop_video_mode()
        cv2.destroyWindow("Video Barcode Reader")

        print("Checkout")
        print(self.barcodeList)

        reader.recycle_instance()


if __name__ == "__main__":

    print("-------------------start------------------------")

    try:
        # Initialize license.
        # Backup License:
        # t0073oQAAAId/dIuBiUjbXGN/R6pq309MFMzLgTtKrcEimfsRTk/geK4uHp6MfkpEuk9yEO/S/gB4qo/qoZ0nA6SeefDZv5oByaMiIQ==
        error = BarcodeReader.init_license("DLS2eyJvcmdhbml6YXRpb25JRCI6IjIwMDAwMSJ9")
        if error[0] != EnumErrorCode.DBR_OK:
            print("License error: " + error[1])

        # Decode video from file or camera
        bcs = BarCodeScanner()
        bcs.run_decode_video()

    except BarcodeReaderError as bre:
        print(bre)

    print("-------------------finished---------------------")