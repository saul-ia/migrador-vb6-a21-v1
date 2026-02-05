const { PrismaClient } = require('@prisma/client');
const prisma = new PrismaClient();

async function main() {
    try {
        const users = await prisma.usuarios.findMany();
        console.log('Users found:', users);

        if (users.length === 0) {
            console.log('No users found. Creating admin...');
            await prisma.usuarios.create({
                data: {
                    Username: 'admin',
                    Password: '123'
                }
            });
            console.log('Admin user created successfully.');
        }
    } catch (e) {
        console.error('Error:', e);
    } finally {
        await prisma.$disconnect();
    }
}

main();
