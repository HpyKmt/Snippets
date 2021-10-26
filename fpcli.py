"""
Command Line Interface of fpath.py
"""
from fpath import *
import sys
import pprint
import time
from functools import partial


__version__ = '0.0.0'


class Cli:
    """ Base """
    WIDTH = 80
    PROMPT = '>>>> '

    def __init__(self, path_in=None, dir_out=None):
        self.path_in = path_in
        self.dir_out = dir_out
        self.fnc_lst = [self.print_help, self.set_path]
        self.cmd = ''

    @classmethod
    def append_fnc(cls, obj, cls_fnc_lst):
        for _cls_fnc in cls_fnc_lst:
            _par_fnc = partial(_cls_fnc, obj)
            _par_fnc.__doc__ = _cls_fnc.__doc__
            obj.fnc_lst.append(_par_fnc)

    # ====================================
    # From here:
    #   Process prompt/loop
    def prompt(self):
        while True:
            # プロンプト
            # 入力待ち状態
            self.cmd = input(self.PROMPT)
            # コマンド入力が来たので処理する。
            if self.cmd:
                self.exe_cmd()
            # 入力が無い場合はループを抜ける。
            else:
                break

    def exe_cmd(self):
        """Execute the command"""
        for fnc in self.fnc_lst:
            if self.cmd == fnc.__doc__.split('\n', 1)[0]:
                fnc()
                break
        else:
            print('ERROR: Unrecognized Command')

    # =============================================
    # From here:
    #   List of functions to be called from prompt/loop
    #
    # Design Rules:
    #   DocString first line: used as command name (max 16 chars)
    #   DocString second line and forth: used as command description
    def print_help(self):
        """Help
Show description of each command."""
        # コマンド名称はDocString一行目に記載。
        # コマンドの詳細はDocString2行目以降に記載。
        # コマンド名称を16文字以内に抑えたい。
        print(self.__class__.__doc__.center(self.WIDTH, '='))
        for fnc in self.fnc_lst:
            if type(fnc.__doc__) == str:
                name, description = fnc.__doc__.split('\n', 1)
                print(f"""{name: <16}: {description}""")
            else:
                raise TypeError(f'ERROR: {fnc} does not have DocString set!')
        print('-' * self.WIDTH)
        print('If you hit enter without entry, the current loop will break.')
        print('=' * self.WIDTH)

    def set_path(self):
        """SetPath
Set path_in and dir_out"""

        # 入力パスを表示して、設定したい場合は設定してもらう。
        print(f'Current Input Path: {self.path_in}')
        if Prompt('Set Input Path?').get_yes_no():
            self.path_in = Prompt('Input file or folder: ').get_file_or_dir()

        # 出力フォルダを表示して、設定したい場合は設定してもらう。
        print(f'Current Output Folder: {self.path_in}')
        if Prompt('Set Output Folder?').get_yes_no():
            self.dir_out = Prompt('Output Folder: ').get_dir()

    @classmethod
    def factory(cls, path_in=None, dir_out=None, cls_fnc_lst=[]):
        obj = cls(path_in=path_in, dir_out=dir_out)
        obj.append_fnc(obj=obj, cls_fnc_lst=cls_fnc_lst)
        return obj


class CliDummy(Cli):
    """ Dummy """

    # =============================================
    # From here:
    #   List of functions to be called from prompt/loop
    def create_dummy_tree(self):
        """Tree
Create a dummy structure by ascendant depth and sibling count."""
        depth = Prompt('How deep?').get_int()
        count = Prompt('How many children?').get_int()
        Dummy.dummy_tree(dir_out=self.dir_out, depth=depth, count=count)

    def create_dummy_file_by_size(self):
        """FileSize
Create a dummy file by the specified byte size."""
        file_size = Prompt('File size (bytes): ').get_int()
        file_name = input('File name: ')
        Dummy.dummy_file_by_size(dir_out=self.dir_out, file_name=file_name, file_size=file_size)


class CliXml(Cli):
    """ XML """

    # =============================================
    # From here:
    #   List of functions to be called from prompt/loop
    def check_file_corruption(self):
        """CheckCorrupt
Check XML File Corruption"""
        # カウンター等の初期化
        success = 0
        failure = 0
        fp_err_lst = []

        # ループ
        for fp in Xml.xml_file_generator(self.path_in):
            obj = Xml(fp)
            if obj.err:
                print(f'File: {fp}')
                print(f'\tError: {obj.err}')
                failure += 1
                # 相対パスを格納する。
                if os.path.isdir(self.path_in):
                    fp_err_lst.append(PathRelative(dir_src=self.path_in, abs_src=fp).rel_src)
            else:
                success += 1

        # 解析結果
        print(f"""Count:
\tSuccess: {success} files
\tFailure: {failure} files
Bad Files:""")
        if len(fp_err_lst) == 0:
            print('\tNone')
        else:
            for fp_err in fp_err_lst:
                print(f'\t{fp_err}')

    def count_element_names(self):
        """CountElements
Count element names"""
        sec = Prompt('Display Interval Seconds(int): ').get_int()

        for fp in Xml.xml_file_generator(self.path_in):
            print(fp)
            obj = Xml(fp)
            if obj.err is None:
                if os.path.isdir(self.path_in):
                    print(f'File: {PathRelative(self.path_in, fp).rel_src}')
                pprint.pprint(obj.count_tag_names())

                for i in range(sec):
                    time.sleep(i)
                    print('.', end='')

                print('\n\n')

    def prettify_utf8(self):
        """Prettify
Format XML and write to file in utf-8 encoding."""
        # 上書き
        over_write = Prompt('Overwrite?').get_yes_no()

        for fp_in in Xml.xml_file_generator(self.path_in):
            obj_xml = Xml(fp_in)
            obj_rel = PathRelative(dir_src=self.path_in, abs_src=fp_in, dir_dst=self.dir_out)
            print(f'processing: {obj_rel.rel_src}')
            # 異常
            if obj_xml.err:
                print(f'ERROR: Format Failure {fp_in}')
            # 正常
            else:
                # 出力用ファイルパスを設定
                if over_write:
                    # 上書きの場合は、入力パスを出力パスにする。
                    fp_out = fp_in
                else:
                    # 中継相対フォルダの構築
                    obj_rel.make_parent_dir()
                    fp_out = obj_rel.abs_dst

                obj_xml.pretty_write_utf8(fp_out)


class CliDelete(Cli):
    """ Delete """

    # =============================================
    # From here:
    #   List of functions to be called from prompt/loop
    def delete_pycache(self):
        """PyCache
Delete __pycache__ folders recursively"""
        Delete.delete_pycache(self.path_in)

    def delete_sub_dirs(self):
        """SubDirBaseName
Delete sub directories by base name"""
        Delete.delete_folders_by_base_name(self.path_in)

    def delete_file_regex(self):
        """FileRegex
Delete files by regular expression"""
        Delete.delete_files_by_regex(self.path_in)


class CliCopy(Cli):
    """ Copy """

    # =============================================
    # From here:
    #   List of functions to be called from prompt/loop
    def by_regex(self):
        """ByRegex
Copy files that match the regular expression """
        dir_in = Prompt('Root Folder: ').eval_dir(self.path_in)
        Copy.copy_files_by_regex(dir_in, self.dir_out)

    def by_modified_date(self):
        """ByModifiedDate
Copy files that were modified after the specified date/time. """
        dir_in = Prompt('Root Folder: ').eval_dir(self.path_in)
        Copy.copy_files_by_modified_timestamp(dir_in, self.dir_out)


class CliMisc(Cli):
    """ Misc """

    # =============================================
    # From here:
    #   List of functions to be called from prompt/loop
    def count(self):
        """Count
Count files folder and file sizes"""
        dir_in = Prompt('Root Folder: ').eval_dir(self.path_in)
        Count.count_files(dir_in)

    # send_toを単体で見れば「@staticmethod」でも良いように見える。
    # しかし、staticmethodにしてしまうと、Cliクラスのexe_cmdの実行でエラーになる。
    # PyCharmはフラグを立てるが、send_toはインスタンスメソッドにしておくこと。
    def send_to(self):
        """SendTo
Create SendTo batch script"""
        SendTo.bat_sendto()


class CliGrep(Cli):
    """ Grep """
    # =============================================
    # From here:
    #   List of functions to be called from prompt/loop

    # staticmethodにしてしまうと、Cliクラスのexe_cmdの実行でエラーになる。
    # PyCharmはフラグを立てるが、インスタンスメソッドにしておくこと。
    def tip(self):
        """Tip
Display helpful regular expression tips"""
        Grep.tip()

    # staticmethodにしてしまうと、Cliクラスのexe_cmdの実行でエラーになる。
    # PyCharmはフラグを立てるが、インスタンスメソッドにしておくこと。
    def test_rgx(self):
        """TestRgx
Test regular expression"""
        Grep.get_regex()

    def grep(self):
        Grep.grep(path_in=self.path_in, dir_out=self.dir_out)


class CliTop(Cli):
    """ Top """

    # function to launch a child CLI prompt
    def launch(self, cls, cls_fnc_lst=[]):
        obj = cls.factory(path_in=self.path_in, dir_out=self.dir_out,
                          cls_fnc_lst=cls_fnc_lst)
        obj.print_help()
        obj.prompt()

    def xml(self):
        """XML
Analyze XML Files"""
        self.launch(cls=CliXml,
                    cls_fnc_lst=[CliXml.prettify_utf8,
                                 CliXml.count_element_names,
                                 CliXml.prettify_utf8])

    def dummy(self):
        """Dummy
Create Dummy Data"""
        self.launch(cls=CliDummy,
                    cls_fnc_lst=[CliDummy.create_dummy_tree,
                                 CliDummy.create_dummy_file_by_size])

    def delete(self):
        """Delete
Delete files or folders"""
        self.launch(cls=CliDelete,
                    cls_fnc_lst=[CliDelete.delete_pycache,
                                 CliDelete.delete_sub_dirs,
                                 CliDelete.delete_file_regex])

    def copy(self):
        """Copy
Copy files"""
        self.launch(cls=CliCopy,
                    cls_fnc_lst=[CliCopy.by_regex,
                                 CliCopy.by_modified_date])

    def grep(self):
        """Grep
Regular Expression search"""
        self.launch(cls=CliGrep,
                    cls_fnc_lst=[CliGrep.tip,
                                 CliGrep.test_rgx])

    def misc(self):
        """Misc
Features you don not use everyday"""
        self.launch(cls=CliMisc,
                    cls_fnc_lst=[CliMisc.count,
                                 CliMisc.send_to])


def entry():
    # SendToがパスを渡していたら、path_in を設定する。
    path_in = None
    if len(sys.argv) == 2:
        if os.path.isfile(sys.argv[1]) or os.path.isdir(sys.argv[1]):
            path_in = sys.argv[1]

    # TopのCommand Line Interfaceを起動する。
    top = CliTop.factory(path_in=path_in,
                         cls_fnc_lst=[CliTop.xml,
                                      CliTop.dummy,
                                      CliTop.delete,
                                      CliTop.copy,
                                      CliTop.misc,
                                      CliTop.grep])
    top.print_help()
    top.prompt()


if __name__ == '__main__':
    entry()
    # SendTo.bat_sendto()
