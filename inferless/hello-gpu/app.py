class InferlessPythonModel:
    def initialize(self):
        print("Initializing")

    def infer(self, inputs: dict):
        print("Inferring")
        number = int(inputs["x"])

        return {"result": f"Your number is {number}"}

    def finalize(self):
        print("Finalizing")
