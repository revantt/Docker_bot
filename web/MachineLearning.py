import os 
import sys
import numpy as np
import pickle
import warnings
warnings.filterwarnings("ignore")
from PIL import Image
from scipy import spatial
from skimage.metrics import structural_similarity as ssim

class classify():
    """class which classifies labels as font differences or other differences using ml"""
    def __init__(self,labelType,containerId):
        self.current_path = os.getcwd()
        if(labelType == "ZPL"):
            self.labelType = 1
        else: 
            self.labelType = 0
        self.actualLabelPath = self.current_path+"/actualLabels/"+containerId+".jpg"
        self.expectedLabelPath = self.current_path+"/expectedLabels/"+containerId+".jpg"
        self.model_path = self.current_path+"/Model/Knn.pkl"

    def load_model(self):
        """Loads the ML model"""
        clf = pickle.load(open(self.model_path, 'rb'))
        return clf

    def get_ssim(self,image1, image2):
        """return structural similarity index"""
        return ssim(image1,image2)
    
    def MSE(self,img1, img2):
        """returns mse between the 2 images"""
        squared_diff = (img1 -img2) ** 2
        summed = np.sum(squared_diff)
        num_pix = img1.shape[0] * img1.shape[1] #img1 and 2 should have same shape
        err = summed / num_pix
        return err

    def get_cosine(self,image1,image2):
        """returns cosine difference b/w the 2 images"""
        return  -1 * (spatial.distance.cosine(image1, image2) - 1)
    
    def get_all_metrics(self):
        """to get all the variables we are using to classify"""
        try:
            fd_size = round(os.path.getsize(self.actualLabelPath)/1000)
            og_size = round(os.path.getsize(self.expectedLabelPath)/1000)
            self.image_size_diff = og_size - fd_size
            image1 = np.asarray(Image.open(self.actualLabelPath))
            image2 = np.asarray(Image.open(self.expectedLabelPath))
            self.ssim = self.get_ssim(image1,image2)
            self.mse = self.MSE(image1,image2)
            image1 = image1.flatten() / 255
            image2 = image2.flatten() / 255
            self.cosineSimilarity = self.get_cosine(image1,image2)
            return [[self.labelType,self.image_size_diff,self.ssim,self.cosineSimilarity,self.mse]]

        except KeyboardInterrupt:
            print("Keyboard interrupt")
            sys.exit(0)

        except:
            return np.nan

    def get_prediction(self):
        """function which returns the prediction"""
        clf = self.load_model()
        all_params = self.get_all_metrics()
        if(not isinstance(all_params,list)):
            return "Image Not Available"
        else:
            pred = clf.predict(all_params)
            if(pred == 1):
                return "other diff"
            elif(pred == 0):
                return "font diff"