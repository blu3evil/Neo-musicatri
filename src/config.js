import axios from 'axios'
const response = await axios.get('/config.json')
export const config = response.data
