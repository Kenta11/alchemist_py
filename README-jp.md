# alchemist-py

alchemistはコンポーネント志向FPGA開発のための開発プラットフォームです．
Python3で実装されています．

## Usage

### プロジェクトの作成

```
$ alchemist new
```

### 設定の反映

```
$ alchemist update
```

### 高位言語レベルシミュレーション

#### 単体テスト

```
$ alchemist test --unit
```

#### 結合テスト

```
$ alchemist test --integration
```

### Bitstreamの生成

```
$ alchemist compile
```

