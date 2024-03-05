class Post(object):
    """
    Creates the input geometry file and calculation directories for the run. Assumes all geometry files are orthogonal
    """
    
    def __init__(self,calcDir,velocity=0.1):  
        
        self.calcDir = calcDir
        #self.ref_file = ref_file
        self.fixed = None
        self.velocity = velocity      
    
    def logdata(self,directory):
        
        logfiles  = natsorted(glob("{}/log.lammps".format(directory)))
        print(logfiles)
        dataset = []

        match_strings = ["Step" ,"Temp" ,"Press" ,"PotEng","Pzz", "f_pull[1]" ,"f_pull[2]", "f_pull[3]", "f_pull[4]", "f_pull[5]" ,"f_pull[6]" ,"f_pull[7]" ,"v_COF", "v_top_load", "v_Papp"]
        for file in logfiles:
            data = open(file,"r").readlines()
            for i,line in enumerate(data):
                
                if all(match in line for match in match_strings):
                    index = i
                    break

            for line in data[i+1:]:
                col = line.split()
                if len(col) == len(match_strings):
                    col = [float(val) for val in col]
                    dataset.append(col)
                else:
                    break

        DF = pd.DataFrame(np.array(dataset),columns=match_strings)

        return DF
