import rospy
import std_srvs
from std_srvs import srv
import handeyecalibration as hec
from handeyecalibration import srv
from handeyecalibration.msg import SampleList
from handeyecalibration.handeye_calibrator import HandeyeCalibrator


class HandeyeServer:
    def __init__(self):
        self.calibrator = HandeyeCalibrator()

        self.get_sample_list_service = rospy.Service(hec.GET_SAMPLE_LIST_TOPIC,
                                                 hec.srv.TakeSample, self.get_sample_lists)
        self.take_sample_service = rospy.Service(hec.TAKE_SAMPLE_TOPIC,
                                                 hec.srv.TakeSample, self.take_sample)
        self.remove_sample_service = rospy.Service(hec.REMOVE_SAMPLE_TOPIC,
                                                   hec.srv.RemoveSample, self.remove_sample)
        self.compute_calibration_service = rospy.Service(hec.COMPUTE_CALIBRATION_TOPIC,
                                                         hec.srv.ComputeCalibration, self.compute_calibration)
        self.save_calibration_service = rospy.Service(hec.SAVE_CALIBRATION_TOPIC,
                                                      std_srvs.srv.Empty, self.save_calibration)

        self.last_calibration = None

    def get_sample_lists(self, req):
        return hec.srv.TakeSampleResponse(SampleList(*self.calibrator.get_visp_samples()))

    def take_sample(self, req):
        self.calibrator.take_sample()
        return hec.srv.TakeSampleResponse(SampleList(*self.calibrator.get_visp_samples()))

    def remove_sample(self, req):
        try:
            self.calibrator.remove_sample(req.sample_index)
        except IndexError:
            rospy.logerr('Invalid index '+req.sample_index)
        return hec.srv.RemoveSampleResponse(SampleList(*self.calibrator.get_visp_samples()))

    def compute_calibration(self, req):
        self.last_calibration = self.calibrator.compute_calibration()
        # TODO: avoid confusion class/msg, change class into HandeyeCalibrationConversions
        ret = hec.srv.ComputeCalibrationResponse()
        ret.calibration.eye_on_hand = self.last_calibration.eye_on_hand
        ret.calibration.transform = self.last_calibration.transformation
        return ret

    def save_calibration(self, req):
        self.last_calibration.to_param()
        self.last_calibration.to_file()
        return std_srvs.srv.EmptyResponse()