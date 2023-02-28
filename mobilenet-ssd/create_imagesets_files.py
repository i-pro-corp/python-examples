'''
Copyright 2023 i-PRO Co., Ltd.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''

'''
[Abstract]
    Create "trainval.txt" and "test.txt" from JPEG files (*.jpg) and annotation files (*.xml).
    JPEGファイル（*.jpg）、アノテーションファイル（*.xml）から "trainval.txt" "test.txt" を作成する。

[Details]
    - Create a file list with only files that exist in both jpeg_path and xml_path.
    - Create a list of class names that exist in all XML files.
    - Create "<class_name>_trainval.txt", "<class_name>_test.txt" for each class. 
      Save 70% of the file to "<class_name>_trainval.txt" and 30% to "<class_name>_test.txt".
    - Randomly shuffle the file name list that collects all "<class_name>_trainval.txt" and save it as "trainval.txt".
    - Randomly shuffle the file name list that collects all "<class_name>_test.txt" and save it as "test.txt".

    - jpeg_path と xml_path の両方に存在するファイルのみでファイルリストを作成する。
    - XML 全ファイル中に存在するクラス名の一覧を作成する。
    - クラス毎に "<class_name>_trainval.txt", "<class_name>_test.txt" を作成する。
      ファイルの 70% を "<class_name>_trainval.txt" に、30% を "<class_name>_test.txt" に保存する。 
    - 全ての "<class_name>_trainval.txt" を集めたファイル名一覧をランダムシャッフルして "trainval.txt" として保存する。
    - 全ての "<class_name>_test.txt" を集めたファイル名一覧をランダムシャッフルして "test.txt" として保存する。

[Author]
    kinoshita hidetoshi (木下英俊)

[library install]
    There should be no libraries that require installation. 
    See the 'import' lines in the source code for the libraries used.

    インストールを必要とするライブラリはないはずです。
    使用しているライブラリついてはソースコード中の 'import' の行を参照。
'''

import argparse
import logging
import sys
import os
import glob
import random
import xml.etree.ElementTree as ET

logging.basicConfig(stream=sys.stdout, level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


'''
[Abstract]
    指定フォルダ中の *.jpg ファイルリストを作成する。
    basename（フォルダパス無し）、拡張子無し、の表記とする。
'''
def create_jpeg_list(folder_path):
    files_with_path = glob.glob(folder_path + "/*.jpg")
    files_without_path_ext = []
    for file in files_with_path:
        files_without_path_ext.append(os.path.splitext(os.path.basename(file))[0])
    return files_without_path_ext


'''
[Abstract]
    Create a list of *.jpg files in the specified folder.
    Use basename (without folder path) and no extension.

    指定フォルダ中の *.xml ファイルリストを作成する。
    basename（フォルダパス無し）、拡張子無し、の表記とする。
'''
def create_xml_list(folder_path):
    files_with_path = glob.glob(folder_path + "/*.xml")
    files_without_path_ext = []
    for file in files_with_path:
        files_without_path_ext.append(os.path.splitext(os.path.basename(file))[0])
    return files_without_path_ext


'''
[Abstract]
    Create a file list that exists in both jpeg_files and xml_files.
    jpeg_files, xml_files の両方に存在するもののみのファイルリストを作成する。
'''
def create_target_list(jpeg_path, xml_path):

    '''
    Create a JPEG file list.
    JPEG ファイル一覧を作成する
    '''
    jpeg_files = create_jpeg_list(jpeg_path)

    '''
    Create a XML file list.
    XML ファイル一覧を作成する
    '''
    xml_files = create_xml_list(xml_path)

    '''
    List files that exist in both JPEG and XML.
    JPEG, XML 両方に共通であるものだけをリスト化    
    '''
    target_files = []
    for file in jpeg_files:
        if file in xml_files:
            target_files.append(file)

    return target_files


'''
[Abstract]
    Output "<class_name>_trainval.txt", "<class_name>_test.txt" for specific class.
    特定クラス向けの "<class_name>_trainval.txt", "<class_name>_test.txt" を出力する
'''
def save_trainval_test_with_class_name(target_files, class_name):
    '''
    Output 70% of file list to "<class_name>_trainval.txt" and 30% to "<class_name>_test.txt".
    ファイルリストの 70% を "<class_name>_trainval.txt" へ、30% を "<class_name>_test.txt" へ出力
    '''
    files_end = len(target_files)
    test_end  = int(files_end * 0.3)

    '''
    Save "<class_name>_test.txt", "<class_name>_trainval.txt".
    '''
    with open( os.path.join( args.imagesets_path, class_name + '_' + args.test_filename), 'w') as f:
        f.write('\n'.join(target_files[0:test_end]))

    with open( os.path.join( args.imagesets_path, class_name + '_' + args.trainval_filename), 'w') as f:
        f.write('\n'.join(target_files[test_end:files_end]))


'''
[Abstract]
    Create "trainval.txt" and "test.txt" from JPEG files (*.jpg) and annotation files (*.xml).
    JPEGファイル（*.jpg）、アノテーションファイル（*.xml）から "trainval.txt" "test.txt" を作成する。
'''
def create_imagesets_files():
    '''
    Create a file list that exists in both jpeg_files and xml_files.
    jpeg_files, xml_files の両方に存在するもののみのファイルリストを作成する。
    '''
    target_files = create_target_list(args.jpeg_path, args.xml_path)

    '''
    create label list.
    ラベルリストを作成
    '''
    label_list = []
    for file in target_files:
        annotation_file = os.path.join( args.xml_path, file + '.xml')
        objects = ET.parse(annotation_file).findall("object")
        for object in objects:
            #class_name = object.find('name').text.lower().strip()
            class_name = object.find('name').text.strip()
            if class_name not in label_list:
                label_list.append(class_name)

    logging.info('=== label_list ===')
    logging.info(label_list)

    '''
    Create trainval_<label>.txt, test_<label>.txt for each label.
    Save file list to trainval_<label>.txt, test_<label>.txt with ratio of 70%, 30%.

    ラベル毎の trainval_<label>.txt, test_<label>.txt を作成
    ファイルリストを 70%, 30% の比率で trainval_<label>.txt, test_<label>.txt へ保存。
    '''
    trainval_files_list = []
    test_files_list = []
    for label in label_list:
        file_list = []
        for file in target_files:
            annotation_file = os.path.join( args.xml_path, file + '.xml')
            objects = ET.parse(annotation_file).findall("object")
            for object in objects:
                class_name = object.find('name').text.strip()
                if class_name == label:
                    file_list.append(file)
                    break
        
        save_trainval_test_with_class_name(file_list, label)
        trainval_files_list.append( label + '_' + args.trainval_filename)
        test_files_list.append( label + '_' + args.test_filename)

    '''
    Randomly shuffle the file name list that collects all "<class_name>_trainval.txt" and save it as "trainval.txt".
    全ての "<class_name>_trainval.txt" を集めたファイル名一覧をランダムシャッフルして "trainval.txt" として保存する。
    '''
    trainval_files = []
    for file in trainval_files_list:
        with open( os.path.join( args.imagesets_path, file), 'r') as f:
             for line in f:
                trainval_files.append(line.strip())

    random.shuffle(trainval_files)
    filename = os.path.join( args.imagesets_path, args.trainval_filename)
    with open( filename, 'w') as f:
        f.write('\n'.join(trainval_files))
        logging.info('=== trainval.txt ===')
        logging.info('path : ' + filename)
        logging.info('size : ' + str(len(trainval_files)))

    '''
    Randomly shuffle the file name list that collects all "<class_name>_test.txt" and save it as "test.txt".
    全ての "<class_name>_test.txt" を集めたファイル名一覧をランダムシャッフルして "test.txt" として保存する。
    '''
    test_files = []
    for file in test_files_list:
        with open( os.path.join( args.imagesets_path, file), 'r') as f:
            for line in f:
                test_files.append(line.strip())

    random.shuffle(test_files)
    filename = os.path.join( args.imagesets_path, args.test_filename)
    with open( filename, 'w') as f:
        f.write('\n'.join(test_files))
        logging.info('=== test.txt ===')
        logging.info('path : ' + filename)
        logging.info('size : ' + str(len(test_files)))


'''
[Abstract]
    main
'''
if __name__ == '__main__':
    parser = argparse.ArgumentParser( description='Create "ImageSets/Main/trainval.txt", "ImageSets/Main.test.txt" files.')
    parser.add_argument("--jpeg_path", default="./data/voc/JPEGImages", type=str, help='Specify JPEGImages (jpeg files) path.')
    parser.add_argument("--xml_path", default="./data/voc/Annotations", type=str, help='Specify Annotations (xml files) path.')
    parser.add_argument("--imagesets_path", default="./data/voc/ImageSets/Main", type=str, help='Specify ImageSets path.')
    parser.add_argument("--trainval_filename", default="trainval.txt", type=str, help='Specify trainval.txt filename.')
    parser.add_argument("--test_filename", default="test.txt", type=str, help='Specify test.txt filename.')
    args = parser.parse_args()

    logging.info('=== args ===')
    logging.info(args)
    
    if os.path.exists( args.jpeg_path ) == False:
        print("NOT exist " + args.jpeg_path + ".")
        sys.exit(1)

    if os.path.exists( args.xml_path ) == False:
        print("NOT exist " + args.xml_path + ".")
        sys.exit(1)

    if os.path.exists( args.imagesets_path ) == False:
        print("NOT exist " + args.imagesets_path + ".")
        sys.exit(1)

    create_imagesets_files()
