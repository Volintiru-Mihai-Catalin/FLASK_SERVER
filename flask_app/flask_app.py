from flask import Flask, request, jsonify, make_response
import psycopg2
from os import environ
from datetime import datetime

app = Flask(__name__)
app.config['SQALCHEMY_DATABASE_URI'] = environ.get('DB_URL')
conn = psycopg2.connect(user=environ.get('DB_USER'),
                        password=environ.get('DB_PASSWORD'),
                        host=environ.get('DB_HOST'),
                        port=environ.get('DB_PORT'),
                        database=environ.get('DB_NAME'))

def represents_int(s):
    try: 
        int(s)
    except ValueError:
        return False
    else:
        return True

@app.route('/test', methods=['GET'])
def test():
    try:
        cursor = conn.cursor()
        cursor.execute('SELECT version();')
        record = cursor.fetchone()
        return make_response(jsonify({'message': record}), 200)
    except Exception as e:
        return make_response(jsonify({'error': str(e)}), 500)
    finally:
        cursor.close()

@app.route('/api/countries', methods=['POST'])
def add_country():
    try:
        cursor = conn.cursor()
        data = request.get_json()
        keys = ['nume', 'lat', 'lon']
        if all(key in data for key in keys):
            cursor.execute("SELECT EXISTS \
                                (SELECT 1 FROM Countries \
                                WHERE country_name = {0});".format("'" + data['nume'] + "'"))
            if cursor.fetchone()[0]:
                return make_response({'message': 'no duplicate countries allowed'}, 409)

            cursor.execute("INSERT INTO Countries(country_name, latitude, longitude) \
                            VALUES ({0}, {1}, {2}) \
                            RETURNING id;".format("'" + data['nume'] + "'", data['lat'], data['lon']))
            conn.commit()
            return make_response(jsonify({'id': cursor.fetchone()[0]}), 201)
        
        return make_response(jsonify({'message': 'bad payload format'}), 400)
    except Exception as e:
        return make_response(jsonify({'error': str(e)}), 500)
    finally:
        cursor.close()

@app.route('/api/countries', methods=['GET'])
def get_countries():
    try:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM Countries;')
        
        list_response = []
        for line in cursor.fetchall():
            id, c_name, lat, lon = line
            list_response.append({'id': id, 'nume': c_name, 'lat': lat, 'lon': lon})
        return make_response(jsonify(list_response), 200)
    except Exception as e:
        return make_response(jsonify({'error': str(e)}), 500)
    finally:
        cursor.close()

@app.route('/api/countries/<int:id>', methods=['PUT'])
def update_country(id):
    try:
        cursor = conn.cursor()
        data = request.get_json()
        keys = ['id', 'nume', 'lat', 'lon']
        
        if all(key in data for key in keys):
            
            # check if the id we want to modify exists
            cursor.execute("SELECT EXISTS \
                                (SELECT 1 FROM Countries \
                                WHERE id = {0});".format(id))
            
            if not cursor.fetchone()[0]:
                return make_response({'message': 'could not find the id to update'}, 404)
            
            # check if the country name already exists
            cursor.execute("SELECT id FROM Countries \
                           WHERE country_name = {0};".format("'" + data['nume'] + "'"))
            result = cursor.fetchone()
            if result:
                if result[0] == id:
                    cursor.execute("UPDATE Countries \
                                    SET country_name = {0}, latitude = {1}, longitude = {2} \
                                    WHERE id = {3};".format("'" + data['nume'] + "'", data['lat'], data['lon'], id))
                    conn.commit()
                    return make_response({}, 200)
                else:
                    return make_response({'message': 'no duplicate countries allowed'}, 409)
            cursor.execute("UPDATE Countries \
                                    SET country_name = {0}, latitude = {1}, longitude = {2} \
                                    WHERE id = {3};".format("'" + data['nume'] + "'", data['lat'], data['lon'], id))
            conn.commit()
            return make_response({}, 200) 
        return make_response(jsonify({'message': 'bad payload format'}), 400)
    except Exception as e:
        return make_response(jsonify({'error': str(e)}), 500)
    finally:
        cursor.close()

@app.route('/api/countries/<int:id>', methods=['DELETE'])
def delete_country(id):
    try:
        cursor = conn.cursor()
        
        cursor.execute("SELECT EXISTS \
                                (SELECT 1 FROM Countries \
                                WHERE id = {0});".format(id))
        if not cursor.fetchone()[0]:
            return make_response({'message': 'country not found'}, 404)

        cursor.execute("DELETE FROM Countries \
                           WHERE id = {0};".format(id))
        conn.commit()
        return make_response({}, 200)
    except Exception as e:
        return make_response(jsonify({'error': str(e)}), 500)
    finally:
        cursor.close()

@app.route('/api/cities', methods=['POST'])
def add_city():
    try:
        cursor = conn.cursor()
        data = request.get_json()
        keys = ['idTara', 'nume', 'lat', 'lon']
        if all(key in data for key in keys):
            cursor.execute("SELECT EXISTS \
                                (SELECT 1 FROM Countries \
                                WHERE id = {0});".format(data['idTara']))
            if not cursor.fetchone()[0]:
                return make_response({'message': 'country not found'}, 404)
            
            cursor.execute("SELECT EXISTS \
                                (SELECT 1 FROM Cities \
                                WHERE city_name = {0});".format("'" + data['nume'] + "'"))
            if cursor.fetchone()[0]:
                return make_response({}, 409)
            
            cursor.execute("INSERT INTO Cities(country_id, city_name, latitude, longitude) \
                            VALUES ({0}, {1}, {2}, {3}) \
                            RETURNING id;".format(data['idTara'], "'" + data['nume'] + "'", data['lat'], data['lon']))
            conn.commit()
            return make_response(jsonify({'id': cursor.fetchone()[0]}), 201)
        return make_response({'message': 'bad payload format'}, 400) 
    except Exception as e:
        return make_response(jsonify({'error': str(e)}), 500)
    finally:
        cursor.close()

@app.route('/api/cities', methods=['GET'])
def get_cities():
    try:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM Cities;')
        
        list_response = []
        for line in cursor.fetchall():
            id, idTara, c_name, lat, lon = line
            list_response.append({'id': id, 'idTara': idTara, 'nume': c_name, 'lat': lat, 'lon': lon})
        return make_response(jsonify(list_response), 200)
    except Exception as e:
        return make_response(jsonify({'error': str(e)}), 500)
    finally:
        cursor.close()

@app.route('/api/cities/country/<int:idTara>', methods=['GET'])
def get_cities_by_country(idTara):
    try:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM Cities WHERE country_id = {0};'.format(idTara))
        list_response = []
        for line in cursor.fetchall():
            id, tara, c_name, lat, lon = line
            list_response.append({'id': id, 'idTara': tara, 'nume': c_name, 'lat': lat, 'lon': lon})
        return make_response(jsonify(list_response), 200)
    except Exception as e:
        return make_response(jsonify({'error': str(e)}), 500)
    finally:
        cursor.close()

@app.route('/api/cities/<int:id>', methods=['PUT'])
def update_city(id):
    try:
        cursor = conn.cursor()
        data = request.get_json()
        keys = ['id', 'idTara', 'nume', 'lat', 'lon']
        if all(key in data for key in keys):
            cursor.execute("SELECT EXISTS \
                                (SELECT 1 FROM Cities \
                                WHERE id = {0});".format(id))
            if not cursor.fetchone()[0]:
                return make_response({'message': 'could not find the id to update'}, 404)
            
            cursor.execute("SELECT EXISTS \
                                (SELECT 1 FROM Countries \
                                WHERE id = {0});".format(data['idTara']))
            if not cursor.fetchone()[0]:
                return make_response({'message': 'country not found'}, 404)

            cursor.execute("SELECT id FROM Cities \
                           WHERE city_name = {0};".format("'" + data['nume'] + "'"))
            result = cursor.fetchone()
            if result:
                if result[0] == id:
                    cursor.execute("UPDATE Cities \
                                    SET country_id = {0}, city_name = {1}, latitude = {2}, longitude = {3} \
                                    WHERE id = {4};".format(data['idTara'], "'" + data['nume'] + "'", data['lat'], data['lon'], id))
                    conn.commit()
                    return make_response({}, 200)
                else:
                    return make_response({'message': 'no duplicate cities allowed'}, 409)
            cursor.execute("UPDATE Cities \
                                    SET country_id = {0}, city_name = {1}, latitude = {2}, longitude = {3} \
                                    WHERE id = {4};".format(data['idTara'], "'" + data['nume'] + "'", data['lat'], data['lon'], id))
            conn.commit()
            return make_response({}, 200)
        return make_response({'message': 'bad payload format'}, 400)
    except Exception as e:
        return make_response(jsonify({'error': str(e)}), 500)
    finally:
        cursor.close()

@app.route('/api/cities/<int:id>', methods=['DELETE'])
def delete_city(id):
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT EXISTS \
                                (SELECT 1 FROM Cities \
                                WHERE id = {0});".format(id))
        if not cursor.fetchone()[0]:
            return make_response({'message': 'city not found'}, 404)

        cursor.execute("DELETE FROM Cities \
                           WHERE id = {0};".format(id))
        conn.commit()
        return make_response({}, 200)
    except Exception as e:
        return make_response(jsonify({'error': str(e)}), 500)
    finally:
        cursor.close()

@app.route('/api/temperatures', methods=['POST'])
def add_temperature():
    try:
        cursor = conn.cursor()
        data = request.get_json()
        keys = ['idOras', 'valoare']
        if all(key in data for key in keys):
            cursor.execute("SELECT EXISTS \
                                (SELECT 1 FROM Cities \
                                WHERE id = {0});".format(data['idOras']))
            if not cursor.fetchone()[0]:
                return make_response({'message': 'city not found'}, 404)
            
            if not represents_int(data['valoare']):
                return make_response({'message': 'bad payload format'}, 400)

            cursor.execute("INSERT INTO Temperatures(val, timestmp, city_id) \
                            VALUES ({0}, '{1}', {2}) \
                           RETURNING id;".format(data['valoare'], str(datetime.now()), data['idOras']))
            conn.commit()
            return make_response(jsonify({'id': cursor.fetchone()[0]}), 201)
        return make_response({'message': 'bad payload format'}, 400)
    except Exception as e:
        return make_response(jsonify({'error': str(e)}), 500)
    finally:
        cursor.close()

@app.route('/api/temperatures', methods=['GET'])
def get_temperatures():
    try:
        cursor = conn.cursor()

        lat = request.args.get('lat')
        lon = request.args.get('lon')
        date_from = request.args.get('from')
        date_until = request.args.get('until')
        
        query = "SELECT t.id, t.val, t.timestmp FROM Temperatures t"
        if lat or lon:
            query += " JOIN Cities c ON c.id = t.city_id WHERE"
            if lat:
                query += " c.latitude = {0} AND".format(lat)
            if lon:
                query += " c.longitude = {0} AND".format(lon)
            query += " TRUE"
        query += ";"
        cursor.execute(query)

        list_response = []
        for line in cursor.fetchall():
            id, val, timestamp = line
            if date_from:
                if date_from > str(timestamp)[:-16]:
                    continue
            if date_until:
                if date_until < str(timestamp)[:-16]:
                    continue
            list_response.append({'id': id, 'valoare': val, 'timestamp': timestamp})
        return make_response(jsonify(list_response), 200)
             
    except Exception as e:
        return make_response(jsonify({'error': str(e)}), 500)
    finally:
        cursor.close()

@app.route('/api/temperatures/cities/<int:idOras>', methods=['GET'])
def get_temperatures_by_city(idOras):
    try:
        cursor = conn.cursor()
        date_from = request.args.get('from')
        date_until = request.args.get('until')

        cursor.execute("SELECT t.id, t.val, t.timestmp FROM Temperatures t\
                       JOIN Cities c ON c.id = t.city_id WHERE c.id = {0};".format(idOras))
        list_response = []
        for line in cursor.fetchall():
            id, val, timestamp = line
            if date_from:
                if date_from > str(timestamp)[:-16]:
                    continue
            if date_until:
                if date_until < str(timestamp)[:-16]:
                    continue
            list_response.append({'id': id, 'valoare': val, 'timestamp': timestamp})
        return make_response(jsonify(list_response), 200)
            
    except Exception as e:
        return make_response(jsonify({'error': str(e)}), 500)
    finally:
        cursor.close()

@app.route('/api/temperatures/countries/<int:idCountry>', methods=['GET'])
def get_temperatures_by_country(idCountry):
    try:
        cursor = conn.cursor()

        date_from = request.args.get('from')
        date_until = request.args.get('until')

        cursor.execute("SELECT t.id, t.val, t.timestmp FROM Temperatures t\
                       JOIN Cities c ON c.id = t.city_id \
                       JOIN Countries h ON h.id = c.country_id \
                       WHERE h.id = {0};".format(idCountry))
        list_response = []
        for line in cursor.fetchall():
            id, val, timestamp = line
            if date_from:
                if date_from > str(timestamp)[:-16]:
                    continue
            if date_until:
                if date_until < str(timestamp)[:-16]:
                    continue
            list_response.append({'id': id, 'valoare': val, 'timestamp': timestamp})
        return make_response(jsonify(list_response), 200)

    except Exception as e:
        return make_response(jsonify({'error': str(e)}), 500)
    finally:
        cursor.close()

@app.route('/api/temperatures/<int:id>', methods=['PUT'])
def update_temp(id):
    try:
        cursor = conn.cursor()
        data = request.get_json()
        keys = ['id', 'idOras', 'valoare']
        if all(key in data for key in keys):
            cursor.execute("SELECT EXISTS \
                                (SELECT 1 FROM Cities \
                                WHERE id = {0});".format(data['idOras']))
            if not cursor.fetchone()[0]:
                return make_response({{'message': 'city not found'}}, 404)
            
            cursor.execute("UPDATE Temperatures \
                           SET val = {0}, timestmp = '{1}', city_id = {2} \
                           WHERE id = {3};".format(data['valoare'], str(datetime.now()), data['idOras'], id))
            conn.commit()
            return make_response(jsonify({}), 200)
        return make_response({'message': 'bad payload format'}, 400)
    except Exception as e:
        return make_response(jsonify({'error': str(e)}), 500)
    finally:
        cursor.close()

@app.route('/api/temperatures/<int:id>', methods=['DELETE'])
def delete_temp(id):
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT EXISTS \
                                (SELECT 1 FROM Temperatures \
                                WHERE id = {0});".format(id))
        if not cursor.fetchone()[0]:
            return make_response({'message': 'temperature entry not found'}, 404)

        cursor.execute("DELETE FROM Temperatures \
                           WHERE id = {0};".format(id))
        conn.commit()
        return make_response({}, 200)
    except Exception as e:
        return make_response(jsonify({'error': str(e)}), 500)
    finally:
        cursor.close()