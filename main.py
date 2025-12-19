from nfl_pipeline import NFLDataPipeline
from constants import SEASONS_TO_EXTRACT

def main():
    seasons = SEASONS_TO_EXTRACT

    data_pipeline = NFLDataPipeline(seasons)
    position_final_data_dict = data_pipeline.run_pipeline(save_extracted=True, save_cleaned=True, save_final=True)

if __name__ == "__main__":
    main()

