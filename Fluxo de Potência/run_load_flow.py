import pandas as pd 
import numpy as np
import pypsa

def mount_network(network_path = None, load_path = None, load_profile = None):
    result_data = []
    network = pypsa.Network()
    network_file = pd.read_excel(network_path)
    load_file = pd.read_excel(load_path)
    profile_file = pd.read_excel(load_profile, usecols=['HORA', 'PERFIL CARGA'])
    set_bus = network_file['De'].tolist() + network_file['Para'].tolist()
    set_bus = list(set(set_bus))
    n_buses = len(set_bus)
    for i in range(1, n_buses+1):
        network.add("Bus","Bus {}".format(i),
                    v_nom = 11)
    for lines in network_file.iterrows():
        line = lines[1]
        bus_from = int(line['De'])
        bus_to = int(line['Para'])
        network.add("Line", f"{bus_from}-{bus_to}",
                    bus0=f"Bus {bus_from}",
                    bus1=f"Bus {bus_to}",
                    x=line['X'],
                    r=line['R'],
                    b=1/line['C'] if line['C'] > 0 else 0)
    for loads in load_file.iterrows():
        load = loads[1]
        bus = int(load['Barra'])
        p = float(load['P'])/1000
        q = float(load['Q'])/1000
        network.add("Load", f"Load {bus}",
                    bus=f"Bus {bus}",
                    p_set = p,
                    q_set = q)
    network.add("Generator","My gen",
            bus="Bus 1",
            control="Slack")
    
    network.loads.q_set *= 0.9
    network.loads.p_set *= 0.9
    for i in range(1, 101):
        aleatory_number = np.random.random()
        for profiles in profile_file.iterrows():
            profile = profiles[1]
            network.loads.q_set *= profile['PERFIL CARGA']*aleatory_number
            network.loads.p_set *= profile['PERFIL CARGA']*aleatory_number
            network.pf()
            df  = network.lines_t.p0.rename(columns = dict(zip(network.lines_t.p0.columns, 'P-' + network.lines_t.p0.columns)))/100
            aux = network.lines_t.q0.rename(columns = dict(zip(network.lines_t.q0.columns, 'Q-' + network.lines_t.q0.columns)))/100
            df = pd.concat([df, aux], axis = 1)
            aux = network.buses_t.v_mag_pu.rename(columns = dict(zip(network.buses_t.v_mag_pu.columns, 'V-' + network.buses_t.v_mag_pu.columns)))
            df = pd.concat([df, aux], axis = 1)
            aux = network.buses_t.v_ang.rename(columns = dict(zip(network.buses_t.v_ang.columns, 'Ang-' + network.buses_t.v_ang.columns)))
            df = pd.concat([df, aux], axis = 1)
            hour = profile['HORA']
            df.index = [f'{i}-{hour}']
            result_data.append(df)
            network.loads.q_set /= profile['PERFIL CARGA']*aleatory_number
            network.loads.p_set /= profile['PERFIL CARGA']*aleatory_number
    
    return pd.concat(result_data, axis = 0)

if __name__ == "__main__":
    data_for_ml = mount_network(network_path='Dados_linha_XXXIV_barras.xlsx', load_path='Cargas_XXXIV_barras.xlsx', load_profile = 'Perfil de Carga_2.xlsx')
    data_for_ml.to_csv('Power_Flow_XXXIV_Bus.csv.gz')
    