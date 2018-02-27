import math
import numpy as np


      unknown_country = [-1.15, -0.17, -0.19, -0.36, 2.01, 0.17, 0.49, -0.85, 0.19, -0.04]

      # countries
      Vietnam = [-0.88, 1.5, 1.03, -1.08, -0.58, 0.19, 0.61, -0.86, -0.24, -0.07]
      England = [-0.02, -1.62, 0.4, -0.63, -0.49, 1.47, -0.64, 0.16, -0.43, -0.13]
      Germany = [-0.21, -0.96, 0.14, -1.13, -0.1, -1.05, -0.31, 0.03, 0.71, -0.29]

      # capitals
      Berlin = [-0.31, -0.96, -0.98, -0.17, -1.05, -1.34, 0.07, 0.04, -0.63, 0.2] # capital of Germany
      Accra = [2.75, 0.86, -0.91, 0.57, 0.1, -0.07, -0.01, -0.12, -0.2, -0.67] # capital of Ghana
      Tokyo = [-1.18, 0.19, -1.59, 0.52, 1.44, 0.08, 0.15, 0.01, -0.26, 0.31] # capital of Japan
      Hanoi = [-0.76, 2.22, -0.69, -0.2, -0.88, 0.31, -0.53, 0.76, 0.25, 0.13] # capital of Vietnam
      Lima = [-0.48, -0.05, 0.93, 2.1, -0.27, -0.19, -0.75, -0.65, 0.19, 0.14] # capital of Peru
      Tehran = [2.66, 1.33, 0.01, -0.04, 0.63, -0.03, 0.07, -0.16, 0.11, -0.27] # capital of Iran

def distance(self, u, v):
      """Calculates a given distance function between vectors u and v"""
      #Implement the distance function between vectors u and v
      #Note: you can also think of this as computing a similarity measure
      #Method: cosine similarity


      cosineSimilarity = 0.0
      uNorm = 0.0
      vNorm = 0.0
      for i in range(len(u)):
          cosineSimilarity += u[i] * v[i]
          uNorm += u[i] * u[i]
          vNorm += v[i] * v[i]
      
      #Normalize - NO NEED TO NORMALIZE
      uNorm = math.sqrt(uNorm)
      vNorm = math.sqrt(vNorm)
      cosineSimilarity = cosineSimilarity / (uNorm * vNorm)

      return cosineSimilarity