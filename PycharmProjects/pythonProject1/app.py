from flask import Flask, request, render_template
import pandas as pd

app = Flask(__name__)

# Load the data
data = pd.read_excel('data.xlsx')


def get_drug_data(drug_name):
    # Strip leading/trailing whitespace and handle case sensitivity
    drug_name = drug_name.strip().lower()
    drug_data = data[data['药物名称'].str.strip().str.lower() == drug_name]
    if not drug_data.empty:
        return drug_data.iloc[0]
    else:
        return None


@app.route('/')
def index():
    return render_template('index.html', error=None)


@app.route('/compare', methods=['POST'])
def compare():
    drug_a = request.form['drug_a']
    drug_b = request.form['drug_b']

    drug_a_data = get_drug_data(drug_a)
    drug_b_data = get_drug_data(drug_b)

    if drug_a_data is None or drug_b_data is None:
        error_message = "One or both drug names not found in the dataset. Please try again."
        return render_template('index.html', error=error_message)

    result = {}

    for column in ['赋值1', '赋值2', '赋值3']:
        value_a = drug_a_data[column]
        value_b = drug_b_data[column]

        if value_a < 6 or value_b < 6:
            impact = '排除'
            difference = 'N/A'  # No need to calculate difference
        else:
            difference = abs(value_a - value_b)
            if difference < 1.2:
                impact = '相互影响'
            elif 1.3 <= difference <= 1.5:
                impact = '弱影响'
            else:
                impact = '明显升高后者血药浓度'

        result[column] = {
            'drug_a_value': value_a,
            'drug_b_value': value_b,
            'difference': difference,
            'impact': impact
        }

    return render_template('result.html', drug_a=drug_a, drug_b=drug_b, result=result)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
