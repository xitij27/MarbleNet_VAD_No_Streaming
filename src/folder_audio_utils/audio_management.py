import numpy as np


class AudioUtils:
    @staticmethod
    def check_overlap(left_list, right_list):
        """
        Checks if there is an overlap between two time intervals for seg

        Args:
            left_list (list): A list in the format [start_time, end_time].
            right_list (list): A list of tuples representing multiple (start_time, end_time) intervals.

        Returns:
            tuple: A tuple containing two values:
                - overlap (bool): True if there is an overlap, False otherwise.
                - offset (float or None): The offset between the start time of the left interval and the
                  correctly identified segment in the right intervals. If no overlap is found, None is returned.
        """
        start_time_left = float(left_list[0])
        end_time_left = float(left_list[1])

        right_array = np.array(right_list)

        overlap_indices = np.where(
            (right_array[:, 1].astype(float) >= start_time_left)
            & (right_array[:, 0].astype(float) <= end_time_left)
        )[0]

        if len(overlap_indices) > 0:
            correctly_identified_segment = right_array[overlap_indices[0]].tolist()
            if start_time_left >= correctly_identified_segment[0]:
                offset = 0.0
            else:
                offset = correctly_identified_segment[0] - start_time_left
                offset = round(offset, 2)
            return True, offset
        else:
            return False, 0.0

    @staticmethod
    def get_label_frame(
        left_list, right_list, sample_rate=16000, frame_duration=0.02, per=0
    ):
        """
        Get labels for time intervals, for frame vad

        Args:
            left_list (list): A list in the format [start_time, end_time].
            right_list (list): A list of tuples representing multiple (start_time, end_time) intervals.
            sample_rate (int): sample rate of audio default 16000
            frame_duration (float): default 20 ms i.e. 0.02s duration (usually in s) of a frame
            per (float): minimum percentage of 1 in a frame to be considered as speech defaults to 0.5

        Returns:
            tuple: A tuple containing two values:
                - overlap (bool): True if there is an overlap, False otherwise.
                - offset (float or None): The offset between the start time of the left interval and the
                  correctly identified segment in the right intervals. If no overlap is found, None is returned.
        """
        start_time_left = float(left_list[0])
        end_time_left = float(left_list[1])
        duration = (end_time_left - start_time_left) * sample_rate
        duration = int(duration)

        data_point_per_frame = int(frame_duration * sample_rate)
        impt_tuples = list(
            filter(
                lambda x: not (x[1] <= start_time_left) | (x[0] >= end_time_left),
                right_list,
            )
        )
        if impt_tuples:
            impt_tuples.sort(key=lambda x: x[0])
            try:
                if impt_tuples[0][0] < start_time_left:
                    impt_tuples[0] = (start_time_left, impt_tuples[0][1])
                if impt_tuples[-1][-1] > end_time_left:
                    impt_tuples[-1] = (impt_tuples[-1][0], end_time_left)
            except Exception as e:
                print(e)

            array_init = np.zeros(duration)
            try:
                for seg in impt_tuples:
                    idx_left_no_adjust = (
                        0 if seg[0] == 0 else (seg[0] * sample_rate) - 1
                    )
                    idx_right_no_adjust = seg[1] * sample_rate
                    idx_left_adjusted = (
                        0
                        if idx_left_no_adjust == 0
                        else idx_left_no_adjust - (start_time_left * 16000 - 1)
                    )
                    idx_right_adjusted = idx_right_no_adjust - (start_time_left * 16000)
                    array_init[int(idx_left_adjusted) : int(idx_right_adjusted)] = 1
            except Exception as e:
                print(f"seg failed with {e}")

            if len(array_init) % data_point_per_frame > 0:
                pad_to_be_added = data_point_per_frame - (
                    len(array_init) % data_point_per_frame
                )
            else:
                pad_to_be_added = 0
            if pad_to_be_added > 0:
                array_padded = np.pad(
                    array_init, (0, pad_to_be_added), "constant", constant_values=0
                )
            else:
                array_padded = array_init
            mean_per_row = array_padded.reshape(-1, data_point_per_frame).mean(axis=1)
            try:
                per = float(per)
            except Exception as e:
                try:
                    print(f"per of {str(per)} can't be converted to float due to {e}")
                    print(
                        "min percentage count of 1 in frame to be considered speech defaults to 0"
                    )
                    per = 0
                except Exception as error:
                    print(error)
            labels = np.where(mean_per_row > per, 1, 0)
            labels = labels.tolist()
            str_form_labels = " ".join(map(str, labels))
        else:
            str_form_labels = " ".join(["0"] * 50)
        return str_form_labels
