import axios from 'axios'
export let config = null
export const initConfig = async () => {
  const response = await axios.get('/config.json')
  config = response.data
}


