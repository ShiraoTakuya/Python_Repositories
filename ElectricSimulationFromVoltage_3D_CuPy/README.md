# 空間電圧電界シミュレーション

SET_VOLTS.csvの設定に基づいて、空間中の電圧と電界をシミュレーションします。
シミュレーション結果はdataフォルダの中に保存されます。
 
# DEMO

空間の電圧分布 
![demo](https://raw.githubusercontent.com/ShiraoTakuya/Python_Repositories/main/ElectricSimulationFromVoltage_3D_CuPy/canvas_electric_voltage_z0050_10000.png)
 
# Features
 
"hoge"のセールスポイントや差別化などを説明する
 
# Requirement
 
以下のライブラリが必要です。

* numpy
* cupy
* time
* glob
* csv
* re
* pandas
* sympy
 
# Usage

以下にシミュレーションしたい条件を指定する
　SET.INI //空間の大きさなど指定
　SET_VOLTS.csv //電極の位置と電圧を指定

以下のコマンドでシミュレーションを実行する。
 
```bash
python source.py
```
 
# Note
 
CUDAが使える環境が必要です。
空間を広くするとシミュレーションに時間がかかります。
電極の配置数を多くすると時間がかかります。
 
# Author
  
ShiraoTakuya
