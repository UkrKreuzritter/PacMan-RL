class pacai_class():
    def __init__(self, stage):
        view_arr = stage.view_field()
        scores = stage.get_number_of_pals_in_each_direction()
        dangers = stage.calculate_danger()
        
        self.arr = [view_arr[0], view_arr[1], view_arr[2], view_arr[3],
                    scores[0], scores[1], scores[2], scores[3],
                    dangers[0], dangers[1], dangers[2], dangers[3]
        ]
    def __str__(self):
        return str(self.arr)