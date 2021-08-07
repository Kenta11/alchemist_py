# Alchemist

AlchemistはDDS(Data Distribution Service)がベースの，コンポーネント指向の高位合成FPGA開発環境です．

## 使い方

### プロジェクトの作成

```
$ alchemist new <project name>
```

### プロジェクトの更新

```
$ alchemist update
```

### 高位言語レベルシミュレーション

#### 単体テスト

```
$ alchemist test --unit <node name>
```

#### 結合テスト

```
$ alchemist test --integration
```

### Bitstreamの生成

```
$ alchemist build
```

## 詳細は

[Common.md](Common.md)をお読み下さい．

