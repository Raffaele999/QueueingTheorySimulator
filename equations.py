

def m_m_inf_server_calcutaion(arrival_rate, service_rate):
    if arrival_rate >= service_rate:
        return 0, ValueError("Arrival rate must be less than service rate")
    # L_q, W_q is obviously 0
    l_q = 0
    w_q = 0
    l_s = arrival_rate / service_rate
    w_s = 1 / service_rate
    
    return w_s, w_q, l_s, l_q