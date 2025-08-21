import { query } from "azle";

export default class BuoyBackend {
    @query()
    hello(name: string): string {
        return `Hello, ${name}!`;
    }
}
