from hashlib import new
import sys , os
import tkinter
from tkinter import filedialog
import re

#変換処理 [レーン、y(なし)、タイミング、なし、音(なし)、終端(ロング):0:0:0:0]
def convert(bpm,path,y,x,first):
    button2.configure(state=tkinter.DISABLED)
    bpm = int(bpm)

    with open(path, 'r', encoding="utf-8") as f:
        osu = f.read().splitlines()

    find = False
    HitObjects = []
    laneList = []
    xLimit = [-9999999,9999999]
    for i in osu: #抽出と分割
        if (i == "[HitObjects]") and (find == False):
            find = True
        elif (find == True) and (i != ''):
            l = []
            for j in re.split('[,:]',i):#キャスト処理
                if j.isdecimal() == True:
                    l.append(int(j))
                else:
                    l.append(str(j))
            HitObjects.append(l)
            if (HitObjects[-1][0] in laneList) == False:
                laneList.append(HitObjects[-1][0])
            if (xLimit[0] < HitObjects[-1][1]):
                xLimit[0] = HitObjects[-1][1]
            if (xLimit[1] > HitObjects[-1][1]):
                xLimit[1] = HitObjects[-1][1]

    laneList = sorted(laneList)
    if first == True:#開始タイミングの調整
        newTiming = 0
        while HitObjects[0][2] > newTiming:
            newTiming = newTiming + (60/bpm*1000)
        newTiming = round(newTiming,5)
        fTiming = newTiming - HitObjects[0][2]

    zerone = []
    for i in HitObjects: #正規化
        timing = round((i[2] + fTiming) / (60/bpm*1000),5)
        lane = laneList.index(i[0]) % 4 + 1
        height = 0
        if (x == True):
            if (y == True) and (i[4] > 0):
                height = (i[1] - xLimit[1]) / (xLimit[0] - xLimit[1]) * 50
            elif (y == False):
                height = (i[1] - xLimit[1]) / (xLimit[0] - xLimit[1]) * 50
        elif (x == False) and (y == True) and (i[4] > 0):
            height = 50
        length = 1
        if i[5] > 0:
            long = round((i[5] + fTiming)/(60/bpm*1000),5)
        else:
            long = "null"
        zerone.append([timing,lane,height,length,long])

    zerone.append([99999999,1,0,1,'null'])
    i = 0
    while i < len(zerone):#終端ロングノーツ追加
        if zerone[i][4] != 'null':
            j = 0
            while (i + j < len(zerone)) and (zerone[i+j][0] < zerone[i][4]):                
                j = j + 1
            zerone.insert(i+j,[zerone[i][4],zerone[i][1],zerone[i][2],1,'null'])
        i = i + 1
    
    i = 0
    while i < len(zerone):#終端ロングノーツ紐づけ
        if zerone[i][4] != 'null':
            j = 0
            while not((zerone[i+j][0] == zerone[i][4]) and (zerone[i+j][1] == zerone[i][1]) and (zerone[i+j][2] == zerone[i][2])):                
                j = j + 1
            zerone[i][4] = i + j + 1
        i = i + 1
    zerone.pop(-1)

    #書き込み
    outputName = "_zerone.txt"
    fpOut = open(os.path.splitext(os.path.basename(path))[0]+outputName,'w')
    fpOut.write('#songname/'+str(bpm)+'/'+str(150 - fTiming)+'\n')
    fpOut.write('*difficulty/0\n')
    for i in zerone:
        fpOut.write(str(i[0])+'/'+str(i[1])+'/'+str(i[2])+'/'+str(i[3])+'/'+str(i[4])+'\n')
    fpOut.close

    success()
    return

#成功表示
def success():
    su = tkinter.Toplevel()
    su.geometry('300x80')
    su.title('SUCCESS!')
    su.resizable(height = False, width = False)
    su.iconphoto(False, tkinter.PhotoImage(file='./pic/ZERONEIIIicon.png'))
    su.grab_set()

    txt4 = tkinter.Label(su,text='変換処理に成功しました',anchor='e', justify='left')
    txt4.place(x=20, y=20)

    button2.configure(state=tkinter.NORMAL)

#異常処理
def error():
    er = tkinter.Toplevel()
    er.geometry('300x80')
    er.title('ERROR')
    er.resizable(height = False, width = False)
    er.iconphoto(False, tkinter.PhotoImage(file='./pic/ZERONEIIIicon.png'))
    er.grab_set()

    txt3 = tkinter.Label(er,text='不明なエラーが発生\n入力値が正しいか確認してください',anchor='e', justify='left')
    txt3.place(x=20, y=20)

    button2.configure(state=tkinter.NORMAL)

#入力規則(数字のみ)
def inputRule(after_word):
    if (after_word.isdecimal() == True) or (after_word == ''):
        return True
    else:
        return False

#ファイル選択+挿入
def fileSelect():
    fp = tkinter.filedialog.askopenfilename(initialdir = './')
    fptb.delete(0,tkinter.END)
    fptb.insert(tkinter.END,fp)
    return

# メイン画面
root = tkinter.Tk()
root.geometry('500x180')
root.title('osu2zerone')
root.resizable(height = False, width = False)
root.iconphoto(False, tkinter.PhotoImage(file='./pic/ZERONEIIIicon.png'))

txt1 = tkinter.Label(text='曲のBPMを入力してください : ')
txt1.place(x=20, y=20)
txt2 = tkinter.Label(text='変換する譜面のファイルを選択してください : ')
txt2.place(x=20, y=70)

bpmtb = tkinter.Entry(width=10)
vcmd1 = (bpmtb.register(inputRule), '%P')
bpmtb.configure(validate='key', vcmd=vcmd1)
bpmtb.place(x=170, y=20)

fptb = tkinter.Entry(width=65)
fptb.place(x=70, y=100)

bln1 = tkinter.BooleanVar()
bln1.set(False)
chk1 = tkinter.Checkbutton(variable=bln1,text='特殊なノーツのみ高さを変更する')
chk1.place(x=260, y=16)

bln2 = tkinter.BooleanVar()
bln2.set(False)
chk2 = tkinter.Checkbutton(variable=bln2,text='x座標を高さとして変換する')
chk2.place(x=260, y=36)

bln3 = tkinter.BooleanVar()
bln3.set(False)
chk3 = tkinter.Checkbutton(variable=bln3,text='開始タイミングを調整する')
chk3.place(x=260, y=56)

button1 = tkinter.Button(text="参照")
button1.configure(command=lambda: fileSelect())
button1.place(x=20, y=97)

button2 = tkinter.Button(text="変換", width=7, height=1, font=("MSゴシック", "13", "bold"))
button2.configure(command=lambda: convert(bpmtb.get(),fptb.get(),bln1.get(),bln2.get(),bln3.get()))
button2.place(x=380, y=135)

root.mainloop()