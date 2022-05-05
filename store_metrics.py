import argparse
import os
import re 
import sqlite3

""" 
take in result.txt and parse results to store in sqlite database 
"""

sqlite3.paramstyle = 'named'

class metricsDB():

    def __init__(self,config=None):
        self.db_path = None
        self.score_path = None
        self.col_names = ['Dataset' ,
        'Method' ,'mae' ,'max_fmeasure' ,'mean_fmeasure' ,'adp_fmeasure' ,'S_measure_alpha05' ,'Fbw_measure' ,'mean_IoU','relax_fmeasure' ]
        self.expr = r"""\[([A-Za-z0-9\- \.\_]+)\]"""
        self.con = None

        for key,val in config.items():
            setattr(self,key,val)
        print(self.db_path)
        print(self.score_path)
    
        if not os.path.exists(self.db_path):
            print("{} not found. A new db will be created".format(self.db_path))
            self.create_new_db()
        
        self._connect()
    
    def insert_results_from_files(self,path=None):
        results_row = self._load_results(path)
        print("{} rows found in file {}".format(len(results_row),path))
        for cur_row in results_row:
            metrics_dict = self._parse_result(cur_row)
            try:
                self._insert_data(metrics_dict)
            except:
                self._update_data(metrics_dict)
        self.con.commit()

    def create_new_db(self):
        con = sqlite3.connect(self.db_path)
        cur = con.cursor()
        
        # Create table
        cur.execute("""CREATE TABLE scores 
                    (Dataset text not null, 
                    Method text not null, 
                    mae real, 
                    max_fmeasure real, 
                    mean_fmeasure real, 
                    adp_fmeasure real, 
                    S_measure_alpha05 real,
                    Fbw_measure real,
                    mean_IoU real,
                    relax_fmeasure real,
                    PRIMARY KEY (Dataset, Method)
                    )
                    """)
        # Insert a row of data
        info_dict = { "dataset": "Tabletennis", 
              "method": "tenergy", 
              "mae": 0.4,
              "max_f_measure": 0.2,
              "mean_f_measure": 0.2,
              "adp_f_measure": 0,
              "s_measure_alpha": 0.9,
              "fbw_measure": 0.6,
              "mean_IoU": 0.59,
              "relax_fmeasure" : 0.6 }

        cur.execute("""INSERT INTO scores 
                    VALUES (
                        :dataset,
                        :method, 
                        :mae,
                        :max_f_measure,
                        :mean_f_measure,
                        :adp_f_measure,
                        :s_measure_alpha,
                        :fbw_measure,
                        :mean_IoU,
                        :relax_fmeasure
                        );
                    """, info_dict)

        # Save (commit) the changes and close
        con.commit()
        con.close()

    def query(self,method=None,dataset=None):
        cur = self.con.cursor()
        if not method and not dataset:
            result = cur.execute("select * from scores")
        elif not method:
            result = cur.execute("select * from scores where Dataset = '{}'".format(dataset))
        elif not dataset:
            result = cur.execute("select * from scores where Method = '{}'".format(method))
        return result
            
    def _parse_result(self,line)->dict:
        metrics_dict = {}
        result = re.findall(self.expr,line)
        for brac in result:
            brac = brac.split(' ')
            brac = [val for val in brac if val]
            col_name = brac[1].replace('-','_')
            score = brac[0]
            if col_name not in ['Dataset','Method']:
                score = float(score)

            metrics_dict[col_name] = score

        # For records that have missing metrics, plug in zero values
        for col_name in self.col_names:
            if not metrics_dict.get(col_name,None):
                metrics_dict[col_name] = 0.0
        return metrics_dict
    
    def _load_results(self,path=None):
        if not path:
            path = self.score_path
        with open(path) as f:
            lines = f.readlines()    
        return lines

    def _update_data(self,metrics_dict):
        print(metrics_dict)
        cur = self.con.cursor()
        cur.execute("""UPDATE scores 
            SET mae = :mae  
            ,max_fmeasure = :max_fmeasure
            ,mean_fmeasure = :mean_fmeasure
            ,adp_fmeasure = :adp_fmeasure
            ,S_measure_alpha05 = :S_measure_alpha05
            ,Fbw_measure = :Fbw_measure
            ,mean_IoU = :mean_IoU
            ,relax_fmeasure = :relax_fmeasure
            WHERE Dataset = :Dataset 
            AND Method = :Method;
            """
            , metrics_dict)

    def _insert_data(self,metrics_dict):
        cur = self.con.cursor()
        cur.execute("""INSERT INTO scores VALUES (
                        :Dataset,
                        :Method, 
                        :mae,
                        :max_fmeasure,
                        :mean_fmeasure,
                        :adp_fmeasure,
                        :S_measure_alpha05,
                        :Fbw_measure,
                        :mean_IoU,
                        :relax_fmeasure
                        )
                    """, metrics_dict)
        print("insertion for {}-{} succeeded".format(metrics_dict['Dataset'],metrics_dict['Method']))
        

    def _connect(self):
       con = sqlite3.connect(self.db_path)
       self.con = con 
       print("created connection")
    


if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--db_path', type=str, default='metrics.db')
    parser.add_argument('--score_path', type=str, default='./score/result.txt')
    config = vars(parser.parse_args())
    print(config)

    # Update the latest result
    new_file = config['score_path']
    thisDB = metricsDB(config)
    thisDB.insert_results_from_files(path=new_file)
