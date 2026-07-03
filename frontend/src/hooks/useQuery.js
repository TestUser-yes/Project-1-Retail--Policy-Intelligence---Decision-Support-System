import { useMutation } from '@tanstack/react-query';
import { queryAPI } from '../services/api';

export const useQuery = () => {
  return useMutation({
    mutationFn: async (data) => {
      const result = await queryAPI.ask(data.query);
      return result;
    },
  });
};
