import sys
import enum
import subprocess

class Op1Type(enum.Enum):
    ADD = '+'
    SUB = '-'

class Op2Type(enum.Enum):
    MUL = '*'
    DIV = '/'

CHAR_OP1 = [
    Op1Type.ADD.value,
    Op1Type.SUB.value,
    ]

CHAR_OP2 = [
    Op2Type.MUL.value,
    Op2Type.DIV.value,
    ]

CHAR_NUM = [str(i) for i in range(10)]

class TokenType(enum.IntEnum):
    OP1 = enum.auto()
    OP2 = enum.auto()
    NUM = enum.auto()

class Token:
    def __init__(self, token_type):
        self.token_type = token_type
        self.num = None
        self.op = None

    def set_num(self, num):
        if num == '':
            self.num = 0
        else:
            self.num = num

    def set_op(self, op):
        self.op = op

    def __repr__(self):
        if self.token_type == TokenType.NUM:
            return f'num:{self.num}'

        if self.token_type == TokenType.OP1:
            return f'op1:{self.op}'
            
        if self.token_type == TokenType.OP2:
            return f'op2:{self.op}'    

def tokenize(expr):
    tokens = []
    buff = ''
    for c in expr:
        if c in CHAR_OP1:
            if buff != '':
                num_token = Token(TokenType.NUM)
                num_token.set_num(int(buff))
                tokens.append(num_token)

            op1_token = Token(TokenType.OP1)
            op1_token.set_op(c)
            tokens.append(op1_token)

            buff = ''

        elif c in CHAR_OP2:
            if buff != '':
                num_token = Token(TokenType.NUM)
                num_token.set_num(int(buff))
                tokens.append(num_token)

            op2_token = Token(TokenType.OP2)
            op2_token.set_op(c)
            tokens.append(op2_token)

            buff = ''

        elif c in CHAR_NUM:
            buff = f'{buff}{c}'
        else:
            raise Exception(f'Invalid charactor: {c}')

    if buff != '':
        num_token = Token(TokenType.NUM)
        num_token.set_num(int(buff))
        tokens.append(num_token)

    return tokens

class Node:
    def __init__(self, token, left, right):
        self.token = token
        self.left = left
        self.right = right

    def __repr__(self):
        return str(self.token)

def create_tree(tokens):
    for i, token in enumerate(tokens):
        if token.token_type == TokenType.OP1:
            return Node(token, create_tree(tokens[:i]), create_tree(tokens[i:][1:]))

    for i, token in enumerate(tokens):
        if token.token_type == TokenType.OP2:
            return Node(token, create_tree(tokens[:i]), create_tree(tokens[i:][1:]))

    return Node(tokens[0], None, None)

# For debug
def print_tree(node, indent=0):
    if node is None:
        return
    for i in range(indent):
        print(' ', end='')
    print(node.token)
    print_tree(node.left, indent+1)
    print_tree(node.right, indent+1)

def write_asm(node, f):
    if node.token.token_type == TokenType.NUM:
        f.write(f'  push {node.token.num}\n')
        return

    write_asm(node.left, f)
    write_asm(node.right, f)

    f.write('  pop rdi\n')
    f.write('  pop rax\n')

    if node.token.token_type == TokenType.OP1:
        if node.token.op == Op1Type.ADD.value:
            f.write('  add rax, rdi\n')
        elif node.token.op == Op1Type.SUB.value:
            f.write('  sub rax, rdi\n')

    elif node.token.token_type == TokenType.OP2:
        if node.token.op == Op2Type.MUL.value:
            f.write('  imul rax, rdi\n')
        elif node.token.op == Op2Type.DIV.value:
            f.write('  cqo\n')
            f.write('  idiv rdi\n')

    f.write('  push rax\n')

def create_asm(tree, asm_name):
    with open(asm_name, 'w') as f:
        f.write('.intel_syntax noprefix\n')
        f.write('.global main\n')
        f.write('main:')

        write_asm(tree, f)

        f.write('  pop rax\n')
        f.write('  ret\n')

def assemble(asm_name, bin_name):
    subprocess.run(['gcc', '-o', bin_name, asm_name])

def run(bin_name):
    run_command = f'./{bin_name}'
    cp = subprocess.run([run_command])

    return cp.returncode

def read_file(fname):
    expr = ''
    with open(fname, 'r') as f:
        for c in f.read():
            if c == '\n':
                break
            expr = f'{expr}{c}'

    return expr

if __name__ == '__main__':
    fname = sys.argv[1]

    expr = read_file(fname)

    print(f'Expression: {expr}')

    tokens = tokenize(expr)
    
    tree = create_tree(tokens)

    #print_tree(tree)

    asm_name = 'calc.s'
    bin_name = 'calc'

    create_asm(tree, asm_name)
    
    assemble(asm_name, bin_name)
    
    rc = run(bin_name)

    print(f'Result: {rc}')

