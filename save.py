import os
import xlwt
import data

class XlsBatch(object):

    def __init__(self, worksheet, head, mode='right'):

        self.worksheet = worksheet
        self.head = head
        self.contents = []
        self.mode = mode

    def move(self, row_add, col_add):

        self.row += row_add
        self.col += col_add
        self.update(self.row, self.col)

    def move_to(self, row_new, col_new):

        self.row = row_new
        self.col = col_new
        self.update(self.row, self.col)

    def update(self, row_new, col_new):

        if row_new > self.row_end:
            self.row_end = row_new

        if col_new > self.col_end:
            self.col_end = col_new

        if row_new < self.row_start:
            self.row_start = row_new

        if col_new < self.col_start:
            self.col_start = col_new

    def render(self, row, col):

        self.row, self.row_start, self.row_end = row, row, row
        self.col, self.col_start, self.col_end = col, col, col

        self.worksheet.write(self.row_start, self.col_start, self.head)
        self.move(1, 0)

        for content in self.contents:

            if type(content) == XlsBatch:

                content.render(self.row, self.col)

                self.update(content.row_start, content.col_start)
                self.update(content.row_end, content.col_end)

                if self.mode == 'right':
                    self.move_to(self.row_start + 1, self.col_end + 1)

                elif self.mode == 'down':
                    self.move_to(self.row_end, self.col_start)

            else:

                for data in content:
                    self.worksheet.write(self.row, self.col, data)
                    self.move(1, 0)


def load(path, ViconDataClass, params=[]):
    files = os.listdir(path)
    files.sort()
    subjects = {}

    for file in files:

        if '.DS_Store' in file:
            continue

        name, condition = file.replace('.csv', '').split(' ', maxsplit=1)

        if name not in subjects:
            subjects[name] = {}

        subjects[name][condition] = ViconDataClass(path + '/' + file, *params)
        print('{} has been loaded'.format(file))

    return subjects


def format_save(subjects, params, mode, save_path):

    for name in subjects:

        workbook = xlwt.Workbook(encoding='ascii')

        for param in params:

            worksheet = workbook.add_sheet(param, cell_overwrite_ok=True)

            param_batch = XlsBatch(worksheet, param)
            subject_batch = XlsBatch(worksheet, name)
            subject_batch.mode = 'down'
            param_batch.contents.append(subject_batch)

            for condition in subjects[name]:

                condition_batch = XlsBatch(worksheet, condition)
                subject_batch.contents.append(condition_batch)

                if mode == 'joints':
                    data = subjects[name][condition].joints

                else:
                    data = subjects[name][condition].model_outputs

                try:
                    for gait_num in range(len(data)):

                        gait_batch = XlsBatch(worksheet, 'Gait ' + str(gait_num))
                        condition_batch.contents.append(gait_batch)

                        for sub_param in data[gait_num][param]:

                            sub_param_batch = XlsBatch(worksheet, sub_param)
                            gait_batch.contents.append(sub_param_batch)
                            sub_param_batch.contents.append(data[gait_num][param][sub_param])

                except:
                    print('Warning: {} - {} - {} of subject {} seems broken'.format(condition, mode, param, name))

            param_batch.render(0, 0)

        save_file = save_path + '/' + name + ' ' + mode + '.xls'
        workbook.save(save_file)
        print('/{} has been outputed'.format(save_file))


if __name__ == "__main__":
    joints = [
        'Head_Head_End',
        'L_Collar_L_Humerus',
        'L_Elbow_L_Wrist',
        'L_Femur_L_Tibia',
        'L_Foot_L_Toe',
        'L_Humerus_L_Elbow',
        'L_Tibia_L_Foot',
        'L_Wrist_L_Wrist_End',
        'LowerBack_Head',
        'LowerBack_L_Collar',
        'LowerBack_R_Collar',
        'R_Collar_R_Humerus',
        'R_Elbow_R_Wrist',
        'R_Femur_R_Tibia',
        'R_Foot_R_Toe',
        'R_Humerus_R_Elbow',
        'R_Tibia_R_Foot',
        'R_Wrist_R_Wrist_End',
        'Root_L_Femur',
        'Root_LowerBack',
        'Root_R_Femur',
        'World_Root'
    ]

    model_outputs = [
        'CentreOfMass',
        'LAnkleAngles',
        'LAnkleForce',
        'LAnkleMoment',
        'LAnklePower',
        'LFootProgressAngles',
        'LGroundReactionForce',
        'LGroundReactionMoment',
        'LHipAngles',
        'LHipForce',
        'LHipMoment',
        'LHipPower',
        'LKneeAngles',
        'LKneeForce',
        'LKneeMoment',
        'LKneePower',
        'LNormalisedGRF',
        'LPelvisAngles',
        'RAnkleAngles',
        'RAnkleForce',
        'RAnkleMoment',
        'RAnklePower',
        'RFootProgressAngles',
        'RGroundReactionForce',
        'RGroundReactionMoment',
        'RHipAngles',
        'RHipForce',
        'RHipMoment',
        'RHipPower',
        'RKneeAngles',
        'RKneeForce',
        'RKneeMoment',
        'RKneePower',
        'RNormalisedGRF',
        'RPelvisAngles'
    ]

    subjects = load('subjects', data.ViconData_interp, [100, 50])

    # subjects = load('subjects', data.ViconData)

    format_save(subjects, joints, 'joints', 'outputs')
    format_save(subjects, model_outputs, 'model_outputs', 'outputs')

    '''
    # Show file names.
    files = os.listdir('subjects')
    files.sort()
    for file in files:
        print(file)
    '''