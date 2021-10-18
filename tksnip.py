import tkinter as tk
from functools import partial


class FncExeBtn:
    """
    ユーザーに実行するFunctionを選ばせる使い捨てボタンの雛形。
    Dictionaryのキーはボタン表示用テキストで値はFunctionオブジェクト.
    Functionに引数は渡せない。
    Functionは実行するだけでReturnはできない。
    """
    def exe_kill(self, fnc):
        """ファンクションを実行する前にGUIを消す。"""
        print('Start of Function:', fnc.__name__)
        self.top.destroy()
        fnc()
        print('End of Function:', fnc.__name__)

    def __init__(self,
                 root=None,
                 title='Select a Function',
                 name_fnc={'Hello World': lambda: print('Hello World'),
                           'Good Morning': lambda: print('*' * 30)}):

        # 必要に応じて親を作成する。
        if root is None:
            self.top = tk.Tk()
        else:
            self.top = tk.Toplevel(root)

        # タイトルを作ってタイトルが表示できる程度の最低限の幅を取る。
        self.top.title(title)
        self.top.minsize(300, 100)

        # ボタンを加える。
        # ボタンの大きさ・幅を統一すると雨にfill=tk.BOTHを設定する。
        for txt, fnc in name_fnc.items():
            tk.Button(self.top, text=txt, command=partial(self.exe_kill, fnc)).pack(fill=tk.BOTH)

        # 親が渡されなかった場合は、自作の親をメインループを作る。
        if root is None:
            self.top.mainloop()


def _test():
    FncExeBtn()


if __name__ == '__main__':
    _test()
