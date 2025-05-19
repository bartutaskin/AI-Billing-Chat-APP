using Ocelot.DependencyInjection;
using Ocelot.Middleware;

namespace MobileProviderApiGateway
{
    public class Program
    {
        public static async Task Main(string[] args)
        {
            var builder = WebApplication.CreateBuilder(args);

            builder.Configuration.AddJsonFile("ocelot.json", optional: false, reloadOnChange: true);
            builder.Services.AddOcelot();

            // Add services to the container.
            builder.Services.AddControllers();
            builder.Services.AddEndpointsApiExplorer();
            builder.Services.AddSwaggerGen();

            // Add CORS policy
            builder.Services.AddCors(options =>
            {
                options.AddPolicy("AllowReactApp", policy =>
                {
                    policy.WithOrigins("http://localhost:3000")
                          .AllowAnyHeader()
                          .AllowAnyMethod();
                });
            });

            var app = builder.Build();

            

            app.UseHttpsRedirection();

            // Enable CORS with your policy before Ocelot middleware
            app.UseCors("AllowReactApp");

            app.UseAuthorization();

            app.MapControllers();

            // Await UseOcelot as last middleware before app.Run()
            await app.UseOcelot();

            app.Run();
        }
    }
}
