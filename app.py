# app.py

from flask import Flask, render_template, request
import math # Diperlukan untuk faktorial (n!) di model M/M/s

app = Flask(__name__)

# --- FUNGSI KALKULASI M/M/1 ---
def analyze_m_m_1_queue(lam, mu):
    if lam >= mu:
        return {"error": "Tingkat kedatangan (λ) harus lebih kecil dari tingkat layanan (μ) untuk model M/M/1."}

    rho = lam / mu
    p0 = 1 - rho
    lq = (lam**2) / (mu * (mu - lam))
    ls = lam / (mu - lam)
    wq = lq / lam
    ws = ls / lam

    return {
        "rho": rho, "p0": p0, "lq": lq, "ls": ls,
        "wq_minutes": wq * 60, "ws_minutes": ws * 60, "error": None
    }

# --- FUNGSI KALKULASI M/M/s (BARU) ---
def analyze_m_m_s_queue(lam, mu, s):
    # Validasi input
    if s <= 0:
        return {"error": "Jumlah server (s) harus lebih dari 0."}
    if lam >= (s * mu):
        return {"error": "Tingkat kedatangan (λ) harus lebih kecil dari kapasitas layanan total (s * μ)."}

    # Menghitung parameter dasar
    rho = lam / (s * mu) # Utilisasi rata-rata per server
    r = lam / mu # Rasio kedatangan terhadap layanan

    # Menghitung P0 (probabilitas tidak ada pelanggan)
    sum_part1 = sum([(r**n) / math.factorial(n) for n in range(s)])
    part2 = (r**s) / (math.factorial(s) * (1 - rho))
    p0 = 1 / (sum_part1 + part2)

    # Menghitung metrik kinerja utama
    lq = (((r**(s+1)) / (math.factorial(s-1) * (s-r)**2)) * p0) if s > 1 else ((p0 * (r**s) * rho) / (s * (1-rho)**2))
    lq_alt = (p0 * (lam / mu)**s * rho) / (math.factorial(s) * (1 - rho)**2) # Rumus Erlang C
    
    ls = lq_alt + r
    wq = lq_alt / lam
    ws = wq + (1 / mu)

    return {
        "rho": rho, "p0": p0, "lq": lq_alt, "ls": ls,
        "wq_minutes": wq * 60, "ws_minutes": ws * 60, "error": None
    }

@app.route('/', methods=['GET', 'POST'])
def index():
    results = None
    input_data = {}

    if request.method == 'POST':
        try:
            # Ambil semua data dari form
            model_type = request.form.get('model_type')
            lam = float(request.form.get('lambda'))
            mu = float(request.form.get('mu'))
            s_str = request.form.get('servers')
            
            s = int(s_str) if s_str and s_str.isdigit() else 1

            input_data = {'lambda': lam, 'mu': mu, 'servers': s, 'model': model_type}

            # Panggil fungsi analisis yang sesuai
            if model_type == 'M/M/1':
                results = analyze_m_m_1_queue(lam, mu)
            elif model_type == 'M/M/s':
                results = analyze_m_m_s_queue(lam, mu, s)

        except (ValueError, TypeError):
            results = {"error": "Pastikan semua input diisi dengan angka yang valid."}

    return render_template('index.html', results=results, inputs=input_data)


if __name__ == '__main__':
    app.run(debug=True)