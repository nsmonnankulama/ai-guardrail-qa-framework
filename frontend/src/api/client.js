import axios from 'axios'

const client = axios.create({
  baseURL: '/api',
  timeout: 300000,
})

export default client
