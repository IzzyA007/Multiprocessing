import argparse
from multiprocessing import Pool
import time


def initMatrix(L, seed_string):
    # create an empty matrix of size L x L
    matrix = [[0 for _ in range(L)] for _ in range(L)]

    # fill the matrix
    for i in range(L):
        for j in range(L):
            # calculate the index for the seed string
            index = (i * L + j) % len(seed_string)
            # fill the cell with the corresponding character from the seed string
            matrix[i][j] = {'a': 0, 'b': 1, 'c': 2}[seed_string[index]]
    return matrix


# function to get the sum of the neighbors

def get_sum(matrix, L, i, j):
    total = 0
    for x in range(max(0, i - 1), min(L, i + 2)):
        for y in range(max(0, j - 1), min(L, j + 2)):
            if x != i or y != j:
                total += matrix[x][y]
    return total


# perform 100 steps of the simulation
def simulation(matrixData):
    matrix = matrixData[0]
    start = matrixData[1][0]
    end = matrixData[1][1]

    L = len(matrix)

    # precompute the even, odd, and prime numbers up to L*L*8 (the maximum possible sum of neighbors)
    even = {0, 2, 4, 6, 8, 10, 12, 14, 16}
    prime = {2, 3, 5, 7, 11, 13}

    new_matrix = [[0 for _ in range(L)] for _ in range(end - start)]  # Create a new matrix for the assigned rows

    for i in range(start, end):
        new_row = [0] * L
        for j in range(L):
            total = get_sum(matrix, L, i, j)
            if matrix[i][j] == 0:
                if total in prime:
                    new_row[j] = 0
                elif total in even:
                    new_row[j] = 1
                else:  # total in odd
                    new_row[j] = 2
            elif matrix[i][j] == 1:
                if total in prime:
                    new_row[j] = 1
                elif total in even:
                    new_row[j] = 2
                else:  # total in odd
                    new_row[j] = 0
            else:  # matrix[i][j] == 'c'
                if total in prime:
                    new_row[j] = 2
                elif total in even:
                    new_row[j] = 0
                else:  # total in odd
                    new_row[j] = 1

            new_matrix[i - start] = new_row  # Adjust index to fit the assigned rows
    return new_matrix


# function to perform column summation and decryption
def column_summation(matrix, L):
    sum_of_column = []
    for j in range(L):
        # calculate the sum of the column
        column_sum = sum(matrix[i][j] for i in range(L))
        sum_of_column.append(column_sum)
    return sum_of_column


def decryptLetter(letter, rotationValue):
    rotationString = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!\"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~ "
    currentPosition = rotationString.find(letter)

    return rotationString[(currentPosition + rotationValue) % 95]


def main():
    starttime = time.time()
    """Validates command line arguments."""
    parser = argparse.ArgumentParser(description="validate and process input arguments.")

    # Adding arguments
    parser.add_argument('-i', type=str, help='Input file path', required=True)
    parser.add_argument('-s', type=str, help='Seed string', required=True)
    parser.add_argument('-o', type=str, help='Output file path', required=True)
    parser.add_argument('-p', type=int, default=1, help='Number of processes', required=False)

    argument = parser.parse_args()

    inputPath = argument.i
    seedString = argument.s
    outputPath = argument.o
    Max_Processes = argument.p

    with open(inputPath, 'r') as inputFile:
        inputString = inputFile.read().strip()
    # inputString = "s:j\:'<^Z=/>@}$L)`YW-/I=0Y=+mF`[ul(e-!-)P},T^<X57{;;3#+$FJ}#/_1h%'fV/.W,JrLF^?,*J&1ZU}SR=`b3$&=$WZ=<u1>?P\Q@[*Y-1&_0u;@{.=)3/cY0Q9),-&R"
    # inputString = "Cbhij"
    # seedString = "baccabacca"
    # seedString = "abc"
    # length of the input string
    L = len(inputString)
    matrix = initMatrix(L, seedString)
    poolProcess = Pool(processes=Max_Processes)

    iterations = 100

    # Calculate chunk size based on the length of the matrix or input string
    if L <= 5:
        chunk_size = 1
    elif L <= 135:
        chunk_size = 5
    elif L <= 1000:
        chunk_size = 10
    else:
        chunk_size = 123
    matrix_Datasize = L // chunk_size
    Data = []
    # Divide the rows into chunks
    for start in range(0, len(matrix), chunk_size):
        end = start + chunk_size
        matrixData = [matrix, (start, end)]  # Correct the creation of matrixData here
        Data.append(matrixData)
        # Divide the rows into chunks
    for i in range(iterations):
        final = poolProcess.map(simulation, Data)
        matrix = [value for row in final for value in row]  # Update the matrix for the next iteration
        for j in range(matrix_Datasize):
            Data[j][0] = matrix

    Sum = column_summation(matrix, L)

    final_string = ""

    for j in range(L):
        final_string += decryptLetter(inputString[j], Sum[j])

    print("Project :: R11712482")
    print("Decrypted String: ", final_string)

    with open(outputPath, 'w') as outputFile:
        outputFile.write(final_string)
    endtime = time.time()
    print(endtime - starttime)


if __name__ == '__main__':
    main()