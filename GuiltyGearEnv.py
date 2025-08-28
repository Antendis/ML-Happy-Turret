import torch

if torch.cuda.is_available() == True:
    print("True")

elif torch.cuda.is_available() == False:
    print("False")