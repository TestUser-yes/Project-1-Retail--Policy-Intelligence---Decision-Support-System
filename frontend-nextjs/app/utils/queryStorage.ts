// Query and favorites storage utility

export interface SavedQuery {
  id: string;
  title: string;
  query: string;
  category: string;
  createdAt: Date;
  lastUsed?: Date;
  isFavorite: boolean;
}

const STORAGE_KEY = "saved_queries";

export const queryStorage = {
  // Save a query
  saveQuery: (title: string, query: string, category: string): SavedQuery => {
    const queries = queryStorage.getAllQueries();
    const newQuery: SavedQuery = {
      id: Date.now().toString(),
      title,
      query,
      category,
      createdAt: new Date(),
      isFavorite: false,
    };
    queries.push(newQuery);
    localStorage.setItem(STORAGE_KEY, JSON.stringify(queries));
    return newQuery;
  },

  // Get all saved queries
  getAllQueries: (): SavedQuery[] => {
    const saved = localStorage.getItem(STORAGE_KEY);
    if (!saved) return [];
    try {
      return JSON.parse(saved).map((q: any) => ({
        ...q,
        createdAt: new Date(q.createdAt),
        lastUsed: q.lastUsed ? new Date(q.lastUsed) : undefined,
      }));
    } catch {
      return [];
    }
  },

  // Get favorite queries
  getFavoriteQueries: (): SavedQuery[] => {
    return queryStorage.getAllQueries().filter((q) => q.isFavorite);
  },

  // Delete a query
  deleteQuery: (id: string): void => {
    const queries = queryStorage.getAllQueries().filter((q) => q.id !== id);
    localStorage.setItem(STORAGE_KEY, JSON.stringify(queries));
  },

  // Toggle favorite
  toggleFavorite: (id: string): void => {
    const queries = queryStorage.getAllQueries();
    const query = queries.find((q) => q.id === id);
    if (query) {
      query.isFavorite = !query.isFavorite;
      localStorage.setItem(STORAGE_KEY, JSON.stringify(queries));
    }
  },

  // Record query usage
  recordUsage: (id: string): void => {
    const queries = queryStorage.getAllQueries();
    const query = queries.find((q) => q.id === id);
    if (query) {
      query.lastUsed = new Date();
      localStorage.setItem(STORAGE_KEY, JSON.stringify(queries));
    }
  },

  // Get most used queries
  getMostUsedQueries: (limit: number = 5): SavedQuery[] => {
    return queryStorage
      .getAllQueries()
      .sort(
        (a, b) =>
          (b.lastUsed?.getTime() || 0) - (a.lastUsed?.getTime() || 0)
      )
      .slice(0, limit);
  },
};
