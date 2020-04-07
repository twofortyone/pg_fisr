#### Python packages

- conda install -c anaconda pywin32

### TODO

#### Review

### IEEE33 Bus test case

#### Data

- Closed = 32
- Opened = 5
- Actions = 160
- States = 435897
- Current state = 435986

Para poner una progressbar dentro de otra se puede modificar la posición: 

```python
pbar1 = tqdm(total=100, position=1)
pbar2 = tqdm(total=200, position=0)
```