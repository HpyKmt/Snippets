"""

"""
import os
import shutil
import re
import datetime
from collections import Counter
import sys

from lxml import etree
import pandas as pd


__version__ = '0.0.0'


class Prompt:
    """ Prompt user for file/directory path from console user interface"""

    def __init__(self, msg='Drag and drop your file/folder: '):
        """
        Constructor
        :param msg: message to prompt user to input file or folder.
        """
        self.msg = msg

    def get_file(self):
        while True:
            path_in = input(self.msg).replace('"', '')
            if os.path.isfile(path_in):
                print(f'INFO: {path_in} is a valid file path.')
                return path_in
            else:
                print(f'ERROR: {path_in} is not a valid file path!')

    def get_dir(self):
        while True:
            path_in = input(self.msg).replace('"', '')
            if os.path.isdir(path_in):
                print(f'INFO: {path_in} is a valid directory path.')
                return path_in
            else:
                print(f'ERROR: {path_in} is not a valid directory path!')

    def eval_dir(self, path_in):
        # 渡された「path_in」がStringでフォルダの場合は、そのまま返す。
        if (type(path_in) == str) and os.path.isdir(path_in):
            return path_in
        # 渡された「path_in」がStringでない場合や、Stringでもフォルダで無い場合、フォルダを設定し直す。
        else:
            return Prompt(self.msg).get_dir()

    def get_file_or_dir(self):
        while True:
            path_in = input(self.msg).replace('"', '')
            if os.path.isdir(path_in):
                print(f'INFO: {path_in} is a valid directory path.')
                return path_in
            elif os.path.isfile(path_in):
                print(f'INFO: {path_in} is a valid file path.')
                return path_in
            else:
                print(f'ERROR: {path_in} is not a valid directory path!')

    def get_regex_i(self):
        # ファイルパスをフィルターする為の簡易正規表現で、大文字小文字の区別はしない。
        while True:
            expr = input(self.msg)
            try:
                # Windowsのファイルシステムは大文字小文字を区別しない。
                # よってファイル検索の場合はCaseを無視するのが適切。
                ptn = re.compile(expr, re.IGNORECASE)
            except re.error as e:
                print('ERROR: failed to compile regular expression!')
                print(e)
            else:
                print('re.compile() was successful')
                return ptn


    def get_dt(self):
        while True:
            expr = input(self.msg)
            ret = DateTime.str_to_dt(expr)
            if ret:
                return ret
            else:
                print('ERROR: Failed to create datetime object!')

    def get_int(self):
        while True:
            expr = input(self.msg)
            try:
                ret = int(expr)
            except ValueError:
                print(f'ERROR: Failed to convert {expr} to an integer.')
            else:
                return ret

    def get_float(self):
        while True:
            expr = input(self.msg)
            try:
                ret = float(expr)
            except ValueError:
                print(f'ERROR: Failed to convert {expr} to a float.')
            else:
                return ret

    def get_yes_no(self):
        while True:
            result = input(f'{self.msg} 1=Yes 0=No: ')
            if result == '1':
                return True
            elif result == '0':
                return False
            else:
                print(f'ERROR: {result} is not a valid entry!')

    def get_list(self):
        while True:
            expr = input(self.msg)
            ret = expr.split()
            print(f"""Result:
\tlength = {len(ret)}
\tlist = {ret}
""")
            if Prompt('Looking good?').get_yes_no():
                return ret


class Mapper:
    """ フォルダをマッピングする。
    効率化の為、returnせずにyieldする。
    変数はファイルを探すか、フォルダを探すか、再帰するか、しないか。"""

    def __init__(self, path_in):
        """
        Constructor
        :param path_in: ファイルもしくはフォルダの絶対パス
        """
        self.path_in = path_in

    def path_generator(self, search_type='file', recursive=True):
        """
        Path Generator
        :param search_type: 'file' or 'dir' as string
        :param recursive: True or False as boolean
        :return: Yield absolute path as string if self.path_in is valid
        Raise ValueError if self.path_in is neither a file nor a folder.
        """
        # 渡されたパスがフォルダであることを確認する。
        if type(self.path_in) == str:
            if os.path.isdir(self.path_in):
                # ファイル
                if search_type == 'file':
                    # 再帰
                    if recursive:
                        for root, dirs, files in os.walk(self.path_in):
                            for file in files:
                                yield os.path.join(root, file)
                    # 子階層のみ
                    else:
                        for i in os.listdir(self.path_in):
                            p = os.path.join(self.path_in, i)
                            if os.path.isfile(p):
                                yield p
                # フォルダ
                elif search_type == 'dir':
                    # 再帰
                    if recursive:
                        for root, dirs, files in os.walk(self.path_in):
                            for sub_dir in dirs:
                                yield os.path.join(root, sub_dir)
                    # 子階層のみ
                    else:
                        for i in os.listdir(self.path_in):
                            p = os.path.join(self.path_in, i)
                            if os.path.isdir(p):
                                yield p
            # 渡されたパスがファイルの場合
            elif os.path.isfile(self.path_in):
                yield self.path_in
            # 渡されたパスがファイルでもフォルダでも無い場合
            else:
                print('ERROR: Passed string is not a valid file or folder!')
                sys.exit()
        else:
            print(f'ERROR: String is expected as a file path. Type was {type(self.path_in)}!')


class Filter:
    """ 通常はファイルやフォルダの名称や拡張子で目的のファイルを取得する.
    複雑な場合は正規表現を使って選別する。"""
    @staticmethod
    def by_base_name(path_in, base_name='__pycache__', search_type='dir', recursive=True):
        """
        Search file or folder by base name
        :param path_in: Parent Folder
        :param base_name: file name or folder name (case insensitive)
        :param search_type: 'file' | 'dir'
        :param recursive: True | False
        :return: Absolute Path
        """
        for fp in Mapper(path_in).path_generator(search_type=search_type, recursive=recursive):
            if os.path.basename(fp).upper() == base_name.upper():
                yield fp

    # @staticmethod
    # def by_extension(path_in, extension='.txt', recursive=True):
    #     """
    #     Search files by extension
    #     :param path_in: parent folder
    #     :param extension:
    #         File extension with dot e.g. '.txt'.
    #         Empty string in case of no extension e.g. ''
    #     :param recursive: True | False
    #     :return: absolute file path
    #     """
    #     for fp in Mapper(path_in).path_generator(search_type='file', recursive=recursive):
    #         if os.path.splitext(fp)[1].upper() == extension.upper():
    #             yield fp

    @staticmethod
    def by_regex(path_in, pattern=re.compile('.*', re.IGNORECASE), search_type='file', recursive=True):
        """
        Search files or folders by regular expression
        :param path_in: parent folder
        :param pattern: compiled regular expression
            If you use regular expression .*ext, it practically functions as endswith.
        :param search_type: 'file' | 'dir'
        :param recursive: True | False
        :return: absolute file or folder path
        """
        for fp in Mapper(path_in).path_generator(search_type=search_type, recursive=recursive):
            if pattern.match(fp):
                yield fp

    @staticmethod
    def by_modified_time(path_in, ts_min=0.0, search_type='file', recursive=True):
        for fp in Mapper(path_in).path_generator(search_type=search_type, recursive=recursive):
            if os.path.getmtime(fp) > ts_min:
                yield fp


class Sorter:
    @staticmethod
    def sort_by_date_modified(fp_gen):
        """
        Sort path by file modified date in ascending order
        :return: yield a path
        """
        for m_time, fp in sorted([(os.path.getmtime(fp), fp) for fp in fp_gen]):
            yield fp


class DateTime:
    FORMATS = [
        # with / and :
        '%Y/%m/%d %H:%M:%S',
        '%Y/%m/%d %H:%M:%S.%f',

        # with - and :
        '%Y-%m-%d %H:%M:%S',
        '%Y-%m-%d %H:%M:%S.%f',

        # with / and :
        # %y (2 digit year)
        '%y/%m/%d %H:%M:%S',
        '%y/%m/%d %H:%M:%S.%f',

        # without
        '%Y%m%d%H%M%S',
        '%Y%m%d%H%M%S%f']

    @classmethod
    def str_to_dt(cls, s):
        """ convert string to datetime object """
        for fmt in cls.FORMATS:
            try:
                dt = datetime.datetime.strptime(s, fmt)
            except ValueError:
                pass
            else:
                print(f'INFO: {s} was parsed successfully.')
                return dt
        else:
            print(f'ERROR: {s} did not get parsed within specified formats!')
            return None

    @classmethod
    def str_to_ts(cls, s):
        """ convert string to timestamp float """
        dt = cls.str_to_dt(s)
        return dt.timestamp()


class Xml:
    def __init__(self, fp_in):
        # ファイルを開いてパーシングする
        try:
            f = open(fp_in, 'rb')
            t = etree.parse(f)
        # 失敗したらエラーメッセージを格納する。
        except etree.XMLSyntaxError as e:
            print(f"""ERROR: failed to parse {fp_in}.""")
            self.tree = None
            self.err = e
        # 成功したらElementオブジェクトを格納する。
        else:
            self.tree = t
            self.err = None
        # 最後にファイルを閉じる。
        finally:
            f.close()

    def pretty_write_utf8(self, fp_out):
        # UTF8でファイルに書き出す。
        if self.tree:
            data = etree.tostring(self.tree, pretty_print=True, xml_declaration=True, encoding='utf-8')
            with open(fp_out, 'wb') as f:
                f.write(data)
        else:
            print(f'ERROR: Cannot write file. self.tree is None.')

    def count_tag_names(self):
        # Elementの名前を集計する。
        tags = [i.tag for i in self.tree.xpath('//*')]
        return Counter(tags)

    @staticmethod
    def pretty(fp):
        try:
            f = open(fp, 'rb')
            tree = etree.parse(f)

        # 「None」が返されたらXMLのファイルが壊れているということ。
        except etree.XMLSyntaxError as e:
            print(f"""ERROR: failed to parse {fp}.
\t{e}""")
            return None

        # パーシングに成功したらフォーマット済みの文字列データを返す。
        # 要注意： 関数の名前は、tostring()だが、返すデータタイプはバイトである。
        # よって、ファイルに書き出す時は open(fp, 'w')ではなく、open(fp, 'w')にする必要がある。
        else:
            return etree.tostring(tree, pretty_print=True, encoding='utf-8', xml_declaration=True)

        # 最後にファイルを閉じる。
        finally:
            f.close()

    @staticmethod
    def xml_file_generator(path_in):
        for fp in Filter.by_regex(path_in=path_in, pattern=re.compile('.*xml', re.IGNORECASE)):
            yield fp

    @staticmethod
    def format_files(path_in=None):
        # XML ファイルの格納された親フォルダを取得する。
        if path_in is None:
            path_in = Prompt('Folder with XML files or XML file: ').get_file_or_dir()

        # 上書きしない場合は出力フォルダを取得する。
        over_write = Prompt('Overwrite?').get_yes_no()
        if over_write:
            dir_out = None
        else:
            dir_out = Prompt('Output Folder: ').get_dir()

        # カウンター
        good = 0
        bad = 0
        bad_lst = []

        # 入力がファイルの場合
        if os.path.isfile(path_in):
            # ファイルを読み込む
            ret = Xml.pretty(path_in)
            fp_in = path_in
            if ret is None:
                bad += 1
                bad_lst.append(fp_in)
            else:
                good += 1
                # 上書きするか？により出力先のファイルを決定する。
                if over_write:
                    fp_out = fp_in
                else:
                    fp_out = os.path.join(dir_out, os.path.basename(fp_in))
                # ファイルに書き込みする。
                with open(fp_out, 'wb') as f:
                    f.write(ret)

        # 入力がフォルダの場合
        elif os.path.isdir(path_in):
            dir_in = path_in
            # ループ
            for fp_in in Filter.by_regex(dir_in, pattern=re.compile('.*xml', re.IGNORECASE)):
                # ファイルを読み込む
                ret = Xml.pretty(fp_in)
                if ret is None:
                    bad += 1
                    bad_lst.append(fp_in)
                else:
                    good += 1
                    # 上書きするか？により出力先のファイルを決定する。
                    if over_write:
                        fp_out = fp_in
                    else:
                        rp = PathRelative(dir_src=dir_in, abs_src=fp_in, dir_dst=dir_out)
                        fp_out = rp.abs_dst

                        # 中間フォルダを作る。
                        rp.make_parent_dir()

                    # ファイルに書き込みする。
                    with open(fp_out, 'wb') as f:
                        f.write(ret)

        # 入力がファイルの場合
        else:
            raise ValueError(f'ERROR: {path_in} is neither file nor folder!')

        # 集計結果を出力
        print(f"""Count:
\tGood: {good}
\tBad: {bad}""")

        if bad > 0:
            print('Bad Files:')
            for fp in bad_lst:
                print(f'\t{fp}')


class Dummy:
    @staticmethod
    def dummy_tree(dir_out=None, depth=2, count=5):
        # ユーザー入力
        if dir_out is None:
            print('Folder is not set yet.')
            dir_out = Prompt('Output folder: ').get_dir()

        # 渡されたパスがフォルダの場合、フォルダを削除して空フォルダを再構築する。
        if os.path.isdir(dir_out):
            shutil.rmtree(dir_out)
            os.makedirs(dir_out)
        # 渡されたパスがフォルダじゃなければ、そこで終了。
        else:
            print(f'ERROR: {dir_out} is not a valid folder.')
            return

        # ループ
        for i in range(count):
            # 現在の位置確認
            print(f'currently: depth={depth}; index={i}')
            # ファイルを作成
            for ext in ['.txt', '.csv', '.tsv', '_']:
                fp = os.path.join(dir_out, f'{depth}-{i}{ext}')
                with open(fp, 'w') as f:
                    f.write('x')

            # フォルダを作成
            if depth > 0:
                dp = os.path.join(dir_out, f'{depth}-{i}')
                os.makedirs(dp)
                # 再帰
                Dummy.dummy_tree(dp, depth=depth-1, count=count)

    @staticmethod
    def dummy_file_by_size(dir_out=None, file_name='dummy.dat', file_size=1024*1024):
        # Caller側で出力フォルダが設定されていない場合は、ここで設定してもらう。
        if dir_out is None:
            dir_out = Prompt('Root of source folder: ').get_dir()

        # Caller側でファイル名称が指定されなかった場合は、デフォルト設定しておく。
        if file_name == '':
            file_name = 'dummy.dat'

        # ファイルを出力する。
        fp = os.path.join(dir_out, file_name)
        with open(fp, 'wb') as f:
            # 指定されたサイズのファイルを作るため、最後のNullの1バイト分だけ引いておく。
            f.seek(file_size - 1)
            f.write(b'\0')
        print(f'File {fp} has been created.')
        print(f'File size is {os.path.getsize(fp)}.')


class PathRelative:
    def __init__(self, dir_src, abs_src, dir_dst=None):
        # ■　考慮するシナリオ
        # 「abs_src」がファイルの場合（最も一般的な場合）
        # 「abs_src」がフォルダの場合（__pycache__を削除する場合など、サブフォルダをos.walk()した場合）
        # 「dir_src」「abs_src」が同じ場合：「self.path_in」がファイルだった場合。
        #
        # ■　頭の片隅に置いておくこと
        # os.walk()で再帰せず、os.listdir()で直下のみループする場合は、「rel_src_parent」は空になる。

        # ■　Source
        # 「dir_src」は解析対象の入力データが格納された親フォルダ
        # 「abs_src」は「dir_src」下に存在するファイル、もしくはフォルダの絶対パス
        self.dir_src = dir_src
        self.abs_src = abs_src

        # ■　相対パス
        # 「rel_src」は入力データパスの相対パス。
        #      「dir_src」と「abs_src」が同じ場合、つまり、self.path_inがファイルだった場合、
        #      「rel_src」は「abs_src」の親フォルダとする。
        # 「rel_src_parent」は「rel_src」の親フォルダの相対パス
        #      「rel_src_parent」が空の場合は、コピー時に中間フォルダを補充しなくても良いということ。
        #      「dir_src」と「abs_src」が同じ場合、つまり、self.path_inがファイルだった場合、
        #      「rel_src_parent」は空にする。
        if dir_src != abs_src:
            # .strip(os.sep)を忘れて、バックスラッシュがパスの前に付いたままだと
            # 、C:ドライブの直下にpythonが勝手にフォルダを作るので要注意！！！
            self.rel_src = abs_src.replace(dir_src, '').strip(os.sep)
            self.rel_src_parent = os.path.dirname(self.rel_src)
        else:
            self.rel_src = os.path.dirname(abs_src)
            self.rel_src_parent = ''

        # ■　Destination
        # 「dir_dst」は出力先のフォルダ
        # 「abs_dst」は出力用のファイルもしくはフォルダの絶対パス
        if dir_dst:
            self.dir_dst = dir_dst
            self.abs_dst_parent = os.path.join(self.dir_dst, self.rel_src_parent)
            self.abs_dst = os.path.join(self.dir_dst, self.rel_src)

    def __repr__(self):
        return f"""Source:
\tsource folder: {self.dir_src}
\tsource data absolute path: {self.abs_src}
\tsource data relative path: {self.rel_src}
\tsource data relative path parent: {self.rel_src_parent}
Destination:
\tdestination folder: {self.dir_dst}
\tdestination data absolute path: {self.abs_dst}
\tdestination data absolute path parent: {self.abs_dst_parent}
"""

    def make_parent_dir(self):
        # 出力フォルダに中間のフォルダパスを作る。
        if self.rel_src_parent:
            try:
                os.makedirs(self.abs_dst_parent)
            except FileExistsError:
                pass
            else:
                print(f'Created {self.abs_dst_parent}')

    def copy(self):
        # ファイル
        if os.path.isfile(self.abs_src):
            shutil.copy2(self.abs_src, self.abs_dst)
        # フォルダ
        elif os.path.isdir(self.abs_src):
            shutil.copytree(self.abs_src, self.abs_dst)
        # エラー
        else:
            raise ValueError(f'ERROR: {self.abs_src} is neither file nor directory!')

    def make_dirs_and_copy(self):
        self.make_parent_dir()
        self.copy()


class SendTo:
    @staticmethod
    def bat_sendto():
        """バッチスクリプトをSendToフォルダに作る。"""
        # インタープリターのパス
        fp_python = sys.executable
        # 現在実行中のモジュール：もし、fpcli.pyがfpath.pyからimportして実行した場合はcaller/fpcli.pyのモジュール名称になる。
        fp_module = sys.argv[0]
        # SendTo のフォルダ
        dir_sendto = os.path.join(os.getenv('appdata'), 'Microsoft', 'Windows', 'SendTo')
        # バッチスクリプトのファイル名称は現在実行中のモジュール名称から拝借
        fn_bat = os.path.splitext(os.path.basename(fp_module))[0] + '.bat'
        # 出力用の絶対パスを構築する。
        fp_bat = os.path.join(dir_sendto, fn_bat)
        # %Arg1%：SendToの場合は右クリックしたファイルもしくはフォルダ
        script = fr"""@echo off
rem python accepts both slash and backslash as path separator.
set "Python="{fp_python}""
set "Script="{fp_module}""
set "Arg1=%1"
set Statement=%Python% %Script% %Arg1%
%Statement%
pause
"""
        # ファイルへの書き込み
        with open(fp_bat, 'w') as f:
            f.write(script)
        # 完了報告
        print(f'{fp_bat} was created.')
        print(script)


class Copy:
    @staticmethod
    def copy_files_by_regex(dir_in, dir_out):
        # ユーザー入力
        pattern = Prompt('Regular Expression: ').get_regex_i()

        for fp_in in Filter.by_regex(dir_in, pattern=pattern, search_type='file', recursive=True):
            PathRelative(dir_in, fp_in, dir_out).make_dirs_and_copy()

    @staticmethod
    def copy_files_by_modified_timestamp(dir_in, dir_out):
        # ユーザー入力
        dt_lmt = Prompt('File Modified Timestamp: ').get_dt().timestamp()

        for fp_in in Filter.by_modified_time(dir_in, ts_min=dt_lmt):
            PathRelative(dir_in, fp_in, dir_out).make_dirs_and_copy()


class Delete:
    @staticmethod
    def delete_pycache(dir_in):
        for dir_sub in Filter.by_base_name(dir_in, base_name='__pycache__', search_type='dir', recursive=True):
            shutil.rmtree(dir_sub)
            print(f'Deleted {dir_sub}.')

    @staticmethod
    def delete_folders_by_base_name(dir_in):
        base_name = input('Folder Name to be : ')
        for dir_sub in Filter.by_base_name(dir_in, base_name=base_name, search_type='dir', recursive=True):
            shutil.rmtree(dir_sub)
            print(f'Deleted {dir_sub}.')

    @staticmethod
    def delete_files_by_regex(dir_in):
        pattern = Prompt('Regular expression to filter files: ').get_regex_i()
        for fp in Filter.by_regex(dir_in, pattern=pattern, search_type='file', recursive=True):
            try:
                os.remove(fp)
            except FileNotFoundError as e:
                print(e)


class Count:
    @staticmethod
    def count_files(dir_in):

        file_count = 0
        dir_count = 0
        file_size = 0
        if os.path.isdir(dir_in):
            for root, dirs, files in os.walk(dir_in):
                for file in files:
                    file_count += 1
                    file_size += os.path.getsize(os.path.join(root, file))
                for _dir in dirs:
                    dir_count += 1
                    # ">16" means 16 space padding on the left
                    # "," means thousand separator
        print(f"""=== Result ===
File Count  : {file_count:>16,}
File Size   : {file_size:>16,}
Folder Count: {dir_count:>16,}""")


class Grep:
    @staticmethod
    def tip():
        print('Regular Expression Tips'.center(50, '='))
        print(r"""https://docs.python.org/3/library/re.html

Inline Flags
    ====================   =======
    re.A   re.ASCII        ?a
    re.I   re.IGNORECASE   ?i
    re.L   re.LOCALE       ?L
    re.M   re.MULTILINE    ?m
    re.S   re.DOTALL       ?s
    re.X   re.VERBOSE      ?x

Typical Group Expressions
    Bracket 
    \[([^\]]+)\]
    
    Parenthesis
    \(([^\)]+)\)
    
    Integer
    (-\d+|\d+)
    
    Hex
    ((0x[0-9a-fA-F]+|[0-9a-fA-F]+))
""")

    @staticmethod
    def get_regex():
        # 各フラグのON/OFFを確認する。
        def check_flags():
            print(' Flags '.center(40, '='))
            for flg in [re.I, re.M, re.S, re.L, re.X, re.A]:
                print('\t{0:<20}: {1}'.format(flg, bool(flg & ptn.flags)))

        # グループ数を確認する。
        def check_group():
            print(' Groups '.center(40, '='))
            print(f'Group Count: {ptn.groups}')
            print(f'Group Index: {ptn.groupindex}')

        # Compile()でフラグは立てない。
        # ユーザーにInline Flagを表現してもらう。
        while True:
            expr = input('Input regular expression: ')
            try:
                ptn = re.compile(expr)
            except re.error as e:
                print('ERROR: failed to compile regular expression!')
                print(e)
                sys.exit()
            else:
                print('re.compile() was successful')
                check_flags()
                check_group()
                if Prompt('Is this regular expression good?'):
                    return ptn
                else:
                    print('Try again...')

    # ファイルパスのジェネレータ
    @staticmethod
    def fp_generator(path_in):
        # ファイルの場合
        if os.path.isfile(path_in):
            yield path_in
        # フォルダの場合
        elif os.path.isdir(path_in):
            # 正規表現でフィルタ
            ptn = Prompt('Regex to filter files: ').get_regex_i()
            gen = Filter.by_regex(path_in=path_in, pattern=ptn)
            # ファイルタイムスタンプで並べ替え
            if Prompt('Sort by date?').get_yes_no():
                gen = Sorter.sort_by_date_modified(gen)
            # 返す
            for fp in gen:
                yield fp
        # 入力が不正の場合はNoneを返す。
        else:
            yield None

    @staticmethod
    def get_columns(expected_length):
        while True:
            columns = Prompt('Column names sep by space: ').get_list()
            if len(columns) == expected_length:
                return columns
            else:
                print('Input Error: The column count does not agree regular expression group count!')

    @staticmethod
    def grep(path_in, dir_out):
        # ファイルを読み込み時のエンコーディングを設定する。
        encoding = input('encoding: ')

        # テキスト抽出用の正規表現を設定する。
        ptn = Grep.get_regex()

        # ループ
        data = []
        for fp in Grep.fp_generator(path_in):
            print(f'\r{fp}', end='')
            with open(fp, 'r', encoding=encoding, errors='ignore') as f:
                data.extend(ptn.findall(f.read()))

        # グループ設定による分岐
        grp_cnt = ptn.groups
        # グループ設定無し
        if grp_cnt == 0:
            fp_out = os.path.join(dir_out, 'grep.txt')
            with open(fp_out, 'w') as f:
                f.write('\n'.join(data))
                print(f'Created {fp_out}.')
        # グループ設定有り
        elif grp_cnt > 0:
            columns = Grep.get_columns(expected_length=grp_cnt)
            df = pd.DataFrame(data=data, columns=columns)
            fp_out = os.path.join(dir_out, 'grep.csv')
            df.to_csv(fp_out)
            print(f'Created {fp_out}')


class Scramble:
    # TODO パスワード等を保存するテキストファイルをエンコード・デコードし、スクロールテキストWidget上で編集保存できるようにする。
    # TODO ランダムな文字列も作る。
    pass


class Zip:
    # TODO 拡張子を「z0-~z255」にする。数字は各バイトのオフセット数を示す。
    # TODO 通常のZipでZipSubDirも処理できるようにする。
    pass


def _test():
    pass


if __name__ == '__main__':
    _test()
